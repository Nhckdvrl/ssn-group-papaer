// E82 CPU native witness. Imports author skills/Task, never main.js or models.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {once} from 'node:events';

const [repo, out, portText, resumeStateFile, continuationMode] = process.argv.slice(2);
const nativeComposition = continuationMode === 'native-composition';
if (nativeComposition && !resumeStateFile) throw new Error('Native composition must continue a preserved world/inventory');
const port = Number(portText);
const TASK = 'multiagent_crafting_bookshelf_full_plan_requires_ctable__depth_0';
const taskPath = path.join(repo, 'tasks/crafting_tasks/test_tasks/2_agent.json');
const taskData = JSON.parse(fs.readFileSync(taskPath, 'utf8'))[TASK];
const resumeExpected = resumeStateFile ? JSON.parse(fs.readFileSync(resumeStateFile,'utf8')) : null;
const started = Date.now();
fs.mkdirSync(out, {recursive: true});
const eventFile = path.join(out, 'native_events.jsonl');
const emit = (kind, data={}) => fs.appendFileSync(eventFile, JSON.stringify({ms: Date.now()-started, kind, ...data})+'\n');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const nativeImport = relative => import(pathToFileURL(path.join(repo, relative)).href);
const settings = (await nativeImport('settings.js')).default;
settings.host = '127.0.0.1';
settings.port = port;
settings.auth = 'offline';
settings.load_memory = false;
settings.allow_insecure_coding = false;
settings.speak = false;
settings.allow_vision = false;
settings.profiles = ['andy', 'jill'].map(name => {
    const file = path.join(out, name+'_native_name_only.json');
    fs.writeFileSync(file, JSON.stringify({name}));
    return file;
});
const mc = await nativeImport('src/utils/mcdata.js');
const skills = await nativeImport('src/agent/library/skills.js');
const {Task} = await nativeImport('src/agent/tasks/tasks.js');
const {initModes} = await nativeImport('src/agent/modes.js');
const bots = [], agents = [];
let pickupActive = false, pickupBusy = false;
const inventory = bot => Object.fromEntries(bot.inventory.items().map(i => [i.name,
    bot.inventory.items().filter(j => j.name===i.name).reduce((n,j)=>n+j.count,0)]));
const snapshot = label => {
    const data = {label, roles: bots.map((bot,i)=>({name:bot.username, count_id:i,
        position:bot.entity?.position, health:bot.health, food:bot.food,
        inventory:inventory(bot), slots:bot.inventory.slots.filter(Boolean).map(x=>({name:x.name,count:x.count,slot:x.slot})),
        author_validator:agents[i]?.task?.validator?.validate(), skill_output:bot.output}))};
    emit('snapshot', data);
    fs.writeFileSync(path.join(out, label+'.json'),JSON.stringify(data,null,2));
    return data;
};
const timed = async (label, callback, timeout=45000) => {
    emit('skill_start',{label});
    let timer;
    try {
        const result = await Promise.race([callback(), new Promise((_,reject)=>{
            timer=setTimeout(()=>reject(new Error('native skill timeout: '+label)),timeout);
        })]);
        emit('skill_return',{label,result});
        return result;
    } finally {clearTimeout(timer);}
};
const summary = {task_id:TASK, task_source:taskPath, original_task:taskData,
    mode:'scripted native feasibility witness, not model cooperation',
    continuation_mode: nativeComposition ? 'POST-HOC original discard/pickup/craft composition, distinct from giveToPlayer helper' : 'original giveToPlayer helper',
    inference_api_calls:0, gpu_hours:0, success:false, stages:[]};
const cap=setTimeout(()=>{
    summary.exception='global native witness timeout';
    summary.wall_seconds=(Date.now()-started)/1000;
    fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));
    for (const bot of bots) bot.quit();
    process.exit(2);
},170000);
try {
    for (let i=0;i<2;i++) {
        const name=['andy','jill'][i];
        const bot=mc.initBot(name);
        bots.push(bot);
        bot.output='';
        bot.on('error',e=>emit('bot_error',{name,error:String(e.stack||e)}));
        bot.on('kicked',reason=>emit('bot_kicked',{name,reason}));
        bot.on('messagestr',message=>emit('server_message',{name,message}));
        bot.on('playerCollect',(collector,collected)=>emit('player_collect',{
            observer:name,collector:collector.username||collector.id,collected_id:collected.id,
            item:collected.getDroppedItem?.()?.name||null}));
        await timed(name+'_spawn',()=>once(bot,'spawn'),60000);
        await bot.waitForChunksToLoad();
        const agent={name,count_id:i,bot,isIdle:()=>false,prompter:{getInitModes:()=>({cheat:false})}};
        agent.task=new Task(agent,taskPath,TASK);
        initModes(agent);
        agents.push(agent);
    }
    await pause(1000);
    if (!resumeExpected) {
        // Same operator initialization used by author initBotTask: clear then
        // give exact source inventories. No items are created afterwards.
        for (let i=0;i<2;i++) {
            bots[i].chat('/clear '+bots[i].username);
            await pause(200);
            for (const [name,count] of Object.entries(taskData.initial_inventory[String(i)])) {
                bots[i].chat(`/give ${bots[i].username} ${name} ${count}`);
                await pause(200);
            }
        }
        await pause(1000);
        for (const agent of agents) await agent.task.teleportBots();
    }
    await pause(3000);
    summary.initial=snapshot('initial_original_inventory');
    const expected=resumeExpected ? resumeExpected.roles.map(x=>x.inventory) : [taskData.initial_inventory['0'],taskData.initial_inventory['1']];
    summary.resumed_from_preserved_state=resumeStateFile || null;
    summary.exact_initial_inventory = bots.every((bot,i)=>
        JSON.stringify(Object.entries(inventory(bot)).sort())===JSON.stringify(Object.entries(expected[i]).sort()));
    if (!summary.exact_initial_inventory) throw new Error('Native inventory differs from source initialization or preserved prefix');
    if (resumeExpected && !nativeComposition) {
        // One ordinary source movement after the recorded too-close refusal;
        // continue the same saved inventory/world, no reset or seed filtering.
        const moved=await timed('author_space_adjustment_once',()=>skills.moveAwayFromEntity(bots[0],bots[1].entity,6),30000);
        summary.stages.push({stage:'native_space_adjustment_after_failure',author_skill_return:moved});
        snapshot('after_native_space_adjustment');
    }
    // Author item_collecting mode uses pickupNearbyItems. Invoke that same
    // skill on the receiver so the dropped-item handover has a real receiver;
    // no teleport, inventory writes, transfer script or escrow substitutes it.
    pickupActive=!nativeComposition;
    const receiver=bots[1];
    receiver.on('physicsTick',async()=>{
        if (!pickupActive || pickupBusy || !receiver.nearestEntity(e=>e.name==='item' && receiver.entity.position.distanceTo(e.position)<8)) return;
        pickupBusy=true;
        try {await skills.pickupNearbyItems(receiver);} catch(e){emit('pickup_error',{error:String(e)});}
        finally {pickupBusy=false;}
    });
    const transfers=resumeExpected ? inventory(bots[0]) : taskData.initial_inventory['0'];
    for (const [item,count] of Object.entries(transfers)) {
        if (nativeComposition) await bots[0].lookAt(bots[1].entity.position.offset(0,1,0));
        const returned=nativeComposition
            ? await timed('author_discard_'+item,()=>skills.discard(bots[0],item,count))
            : await timed('author_give_'+item,()=>skills.giveToPlayer(bots[0],item,bots[1].username,count));
        await pause(500);
        if (nativeComposition) {
            // The native receiver obtains a dropped world entity, never an
            // inventory write. Wait for any mode pickup already in progress.
            while(pickupBusy) await pause(100);
            await timed('author_pickup_'+item,()=>skills.pickupNearbyItems(receiver));
            await pause(500);
        }
        summary.stages.push({stage:nativeComposition ? 'native_discard_pickup' : 'transfer',item,count,author_skill_return:returned,
            inventories:bots.map(inventory)});
        snapshot('after_transfer_'+item);
    }
    pickupActive=false;
    while(pickupBusy) await pause(100);
    summary.before_craft=snapshot('before_craft');
    summary.craft_return=await timed('author_craft_bookshelf',()=>skills.craftRecipe(bots[1],'bookshelf',1),60000);
    await pause(500);
    summary.final=snapshot('final_before_any_automatic_clear');
    summary.success=summary.final.roles[1].author_validator.valid && inventory(bots[1]).bookshelf>=1;
    emit('completed',{success:summary.success});
} catch(error) {
    summary.exception=String(error.stack||error);
    emit('witness_exception',{error:summary.exception});
    if (bots.every(bot=>bot.inventory && bot.entity)) snapshot('failure_preserved_state');
} finally {
    clearTimeout(cap);
    pickupActive=false;
    summary.wall_seconds=(Date.now()-started)/1000;
    fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));
    for(const bot of bots) bot.quit();
    await pause(500);
    console.log(JSON.stringify({success:summary.success,wall_seconds:summary.wall_seconds,exception:summary.exception}));
    process.exit(summary.success?0:1);
}
