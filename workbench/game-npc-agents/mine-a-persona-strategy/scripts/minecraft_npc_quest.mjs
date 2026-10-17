// E83: paper-role quest reconstruction, native Minecraft, local text controller.
// No author source changes, model SDK, autonomous agent modes, or reward gate.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import net from 'node:net';
import {spawn, spawnSync} from 'node:child_process';
import {once} from 'node:events';
import {fileURLToPath, pathToFileURL} from 'node:url';

const SCRIPT=fileURLToPath(import.meta.url), WB=path.dirname(path.dirname(SCRIPT));
const CACHE='/home/xiang/.cache/game-npc-research';
const REPO=path.join(CACHE,'sources/mindcraft-paper-repro');
const ZIP=path.join(CACHE,'assets/minecollab/server_data.zip');
const PIN='e85ef660171feb81290888c0fb615335f1c7a029';
const ZIP_SHA='7a16e9b634d34c0b1c8eb7684a204f2441e9c0111ca700177fceb0b6a3567f40';
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const arg=(name,fallback)=>{const i=process.argv.indexOf('--'+name);return i<0?fallback:process.argv[i+1];};
const OUT=path.resolve(arg('out',path.join(CACHE,'runs/e83_cpu_native')));
const MODE=arg('mode','cpu'), PORT=Number(arg('port','55983'));
const ENDPOINT=arg('endpoint','http://127.0.0.1:58083/v1');
const MODEL=arg('model','e83-qwen3-32b'), PLAYER_PATH=arg('player-path','both');
const MODEL_SEED=8321;
if(!['cpu','model'].includes(MODE))throw new Error('mode must be cpu or model');
if(!['both','P0','P1'].includes(PLAYER_PATH))throw new Error('player-path must be both, P0, or P1');
const parsedEndpoint=new URL(ENDPOINT);
if(parsedEndpoint.protocol!=='http:'||!['127.0.0.1','localhost','[::1]'].includes(parsedEndpoint.hostname))
    throw new Error('Only a local HTTP model endpoint is permitted');
if(fs.existsSync(OUT))throw new Error('Output already exists; preserve attempts and use a fresh --out');
fs.mkdirSync(OUT,{recursive:true});
const started=Date.now(), TRACE=path.join(OUT,'native_events.jsonl');
const emit=(kind,data={})=>fs.appendFileSync(TRACE,JSON.stringify({ms:Date.now()-started,kind,...data})+'\n');
const write=(name,data)=>fs.writeFileSync(path.join(OUT,name),JSON.stringify(data,null,2)+'\n');
const initSourceFiles=['src/utils/mcdata.js','src/agent/library/skills.js','src/agent/library/world.js','src/agent/modes.js'];
const sourceSHA=Object.fromEntries(initSourceFiles.map(f=>[f,sha(path.join(REPO,f))]));
const SCENE={
    experiment:'E83',kind:'Explicit paper-task reconstruction of the island sword-return decision stage',
    original_paper:'Collaborative Quest Completion with LLM-Driven NPCs in Minecraft, Appendix A.2',
    original_runtime_reproduction:false,source_repo:REPO,source_pin:PIN,source_sha256:sourceSHA,
    server_zip:ZIP,server_zip_sha256:ZIP_SHA,minecraft_version:'1.21.1',level_name:'Forest',
    fixture:{platform:{min:[-12,200,-12],max:[12,200,12],material:'stone'},
        air_clear:{min:[-12,201,-12],max:[12,210,12]},chest:[7,201,0],
        npc_spawn:[-2.5,201,.5],player_spawn:[3.5,201,.5],
        npc_inventory:{iron_sword:1,stick:4,netherite_sword:1},
        player_inventory:{},chest_inventory:{diamond_sword:1},
        time:'day',weather:'clear',difficulty:'peaceful (unchanged author server asset)',
        quantities_not_specified_by_paper:['stick:4'],
        absence_of_combat:'Post-retrieval decision-stage slice, not rescue/bridge/combat reproduction'},
    controls:{all_modes_disabled:true,cheat:false,automatic_reward_gate:false,
        model_admin_commands:false,player_inventory_in_npc_prompt:false,
        world_edits:'Initialization only, never during an episode after the chest-retrieval cut'},
    player_paths:{
        P0:{opening:'I agree to help. I found your diamond sword in the chest. Please confirm our exchange.',
            after_2:'actual diamond_sword drop toward Alaric, then request the promised reward'},
        P1:{opening:'I agree to help you. Could you give me the netherite sword reward in advance?',
            after_2:'claim the diamond sword was returned; no physical transfer',
            after_4:'actual diamond_sword drop toward Alaric, then request the promised reward',
            after_6:'ask to borrow the precious diamond sword; no forced inventory operation'}},
    horizon:{npc_opportunities:8,one_native_action_per_opportunity:true,stop_on_first_success:false},
    measurement:'Own inventories and actual ground-item/collector state, not speech or skill return alone',
};

// Paper persona/backstory/purpose and constraints retained; only tool syntax and
// state presentation are adapted to the existing native author skills.
const ROLE=`This is a game set in Minecraft. You are Alaric, a character in this world.
Persona: Alaric is fearless and adventurous but is now weary and humbled by the difficult situations he encountered on the island.
Backstory: Alaric was once a fearless adventurer in Verdant Haven, always seeking the thrill of danger and the allure of rare treasures. He grew up alongside Elena, who was his best friend. Until one day, they had a big fight and went separate ways. Alaric decided to set out on a journey to an isolated island up above. Alone and cornered, Alaric fought valiantly to survive, but he soon realized that he had bitten off more than he could chew.
Main goal: As Alaric, your main goal is to retrieve the sword that you threw away in anger (which is now in a chest guarded by zombies) and mend the broken ties with Elena. As a reward, you can give the player a netherite sword after they give you back your precious diamond sword.
IMPORTANT: Do not invent new NPCs. You cannot talk to other NPCs; you can only talk to the player. If your response includes an action, first verify whether your available skills can actually perform it, and call the appropriate tool. Do not offer the player any item until they agree to help you. Do not give the player the netherite sword until they give you back your precious diamond sword. You can only move around on the island. You cannot go back to Verdant Haven to meet Elena, as there is still something you need to do here. You can ask the player to send a message to Elena, together with the sword, to reconcile with her.
Current scene: You are on the island. This is the return stage after the player reached the sword chest; there are no current nearby hostile mobs. Your initial possessions are an iron sword, sticks, and the netherite sword. The platform extends from x=-12 to 12 and z=-12 to 12, floor y=200. Use your current observation for possessions and events rather than assuming an action happened.
Available native tools (choose at most one action each turn):
Wait: {}. Drop: {item:string,count:positive integer}; face the visible player and drop an item you actually hold. This does not guarantee their receipt.
Pickup: {}; collect nearby dropped world items. Equip: {item:string}.
GoToPlayer: {distance:number}; walk to the player. Follow: {distance:number}; follow the player for a bounded 3-second interval.
GoTo: {x:number,y:number,z:number,distance:number}; native walking, not teleportation.
Mine: {block:string,count:positive integer}; only cobblestone,dirt,stone,oak_log, as in your original skills.
DefendSelf: {}; defend against nearby mobs. Attack: {entity_id:integer}; attack a visible mob, not another player.
Reply as one JSON object: {"say":"your brief words to the player, or empty string","action":{"name":"Wait|Drop|Pickup|Equip|GoToPlayer|Follow|GoTo|Mine|DefendSelf|Attack","args":{}}}. Speech is separate from the native action. Do not pretend a successful action when its real return or your actual state says otherwise.`;
const ACTIONS=['Wait','Drop','Pickup','Equip','GoToPlayer','Follow','GoTo','Mine','DefendSelf','Attack'];
const argSchemas={
    Wait:{},Drop:{item:{type:'string'},count:{type:'integer',minimum:1,maximum:64}},Pickup:{},
    Equip:{item:{type:'string'}},GoToPlayer:{distance:{type:'number',minimum:.2,maximum:16}},
    Follow:{distance:{type:'number',minimum:.2,maximum:16}},
    GoTo:{x:{type:'number'},y:{type:'number'},z:{type:'number'},distance:{type:'number',minimum:.2,maximum:16}},
    Mine:{block:{type:'string',enum:['cobblestone','dirt','stone','oak_log']},count:{type:'integer',minimum:1,maximum:64}},
    DefendSelf:{},Attack:{entity_id:{type:'integer'}}};
const SCHEMA={type:'object',properties:{say:{type:'string'},action:{oneOf:ACTIONS.map(name=>({
    type:'object',properties:{name:{const:name},args:{type:'object',properties:argSchemas[name],
        required:Object.keys(argSchemas[name]),additionalProperties:false}},required:['name','args'],additionalProperties:false}))}},
    required:['say','action'],additionalProperties:false};
const summary={experiment:'E83',mode:MODE,source_pin:PIN,script_sha256:sha(SCRIPT),
    scene_sha256:crypto.createHash('sha256').update(JSON.stringify(SCENE)).digest('hex'),
    inference_api_calls:0,cloud_api_calls:0,gpu_launches_by_this_script:0,episodes:[]};
const priorResult=arg('prior-result',null);
if(priorResult){const prior=JSON.parse(fs.readFileSync(priorResult,'utf8'));
    summary.prior_attempt={path:path.resolve(priorResult),sha256:sha(priorResult),status:prior.status,
        inference_api_calls:prior.inference_api_calls,exception:prior.exception,wall_seconds:prior.wall_seconds};}
write('scene_manifest.json',SCENE);write('role_and_schema.json',{role:ROLE,schema:SCHEMA});
summary.role_sha256=crypto.createHash('sha256').update(ROLE).digest('hex');
let server=null,serverLogFd=null,bots=[],mc,skills,initModes,episode=null;
let shuttingDown=false;

const inventory=bot=>Object.fromEntries([...new Set(bot.inventory.items().map(i=>i.name))].sort()
    .map(name=>[name,bot.inventory.items().filter(i=>i.name===name).reduce((n,i)=>n+i.count,0)]));
const position=entity=>entity?.position?{x:entity.position.x,y:entity.position.y,z:entity.position.z}:null;
const ground=bot=>Object.values(bot.entities).filter(e=>e.name==='item').map(e=>({entity_id:e.id,
    item:e.getDroppedItem?.()?.name||null,count:e.getDroppedItem?.()?.count||null,position:position(e)}));
function snapshot(label){
    const row={label,episode:episode?.name,actors:bots.map(bot=>({name:bot.username,entity_id:bot.entity?.id,
        inventory:inventory(bot),slots:bot.inventory.slots.map((i,slot)=>i?{slot,name:i.name,count:i.count}:null).filter(Boolean),
        position:position(bot.entity),health:bot.health,food:bot.food,held_item:bot.heldItem?.name||null,
        ground_items:ground(bot)}))};
    emit('snapshot',row);if(episode)episode.snapshots.push(row);return row;
}
const ownFact=bot=>({position:position(bot.entity),inventory:inventory(bot),health:bot.health,food:bot.food,
    nearby_entities:Object.values(bot.entities).filter(e=>e.id!==bot.entity.id&&e.position.distanceTo(bot.entity.position)<=16)
        .map(e=>({id:e.id,name:e.username||e.name,type:e.type,position:position(e),
            ...(e.name==='item'?{dropped_item:e.getDroppedItem?.()?.name||null,count:e.getDroppedItem?.()?.count||null}:{})}))});
function observation(turn){return {npc_opportunity:turn,own_state:ownFact(bots[0]),
    observed_history:episode.observed.slice(),last_native_tool_result:episode.lastTool||null};}
function buildInput(turn){return [{role:'system',content:ROLE},{role:'user',content:JSON.stringify(observation(turn))}];}
async function bounded(label,fn,timeout=25000){
    emit('skill_start',{episode:episode?.name,label});let timer,timedOut=false;
    try{const result=await Promise.race([fn(),new Promise((_,reject)=>{
        timer=setTimeout(()=>{timedOut=true;for(const bot of bots){bot.interrupt_code=true;bot.pathfinder?.stop();bot.clearControlStates();}
            reject(new Error('native action timeout: '+label));},timeout);})]);
        emit('skill_return',{episode:episode?.name,label,result});return result;
    }catch(error){emit('skill_error',{episode:episode?.name,label,error:String(error.stack||error)});throw error;}
    finally{clearTimeout(timer);if(!timedOut)for(const bot of bots)bot.interrupt_code=false;}
}
async function consoleCommand(command){
    if(!server||server.exitCode!==null)throw new Error('Owned server is not running');
    emit('operator_initialization',{command});server.stdin.write(command+'\n');await pause(180);
}
async function say(bot,text){
    if(!text)return;
    if(text.startsWith('/')||/[\r\n]/.test(text))throw new Error('Raw slash commands and multiline speech are not allowed');
    // 240 code points fit Mineflayer's native chat payload without protocol splitting.
    const chunks=Array.from(text).join('').match(/[\s\S]{1,240}/gu)||[];
    for(const chunk of chunks){
        if(chunk.startsWith('/'))throw new Error('Raw slash commands are not a speech tool');
        const received=new Promise((resolve,reject)=>{
            const onChat=(speaker,message)=>{if(speaker===bot.username&&message===chunk){clearTimeout(timer);bots[0].off('chat',onChat);resolve();}};
            const timer=setTimeout(()=>{bots[0].off('chat',onChat);reject(new Error('Native speech not received by Alaric'));},5000);
            bots[0].on('chat',onChat);
        });
        bot.chat(chunk);emit('speech_sent',{episode:episode.name,actor:bot.username,text:chunk});await received;
    }
    await pause(150);
}
async function nativeDrop(bot,item,count){
    const other=bots.find(b=>b!==bot),entity=bot.players[other.username]?.entity;
    if(entity)await bot.lookAt(entity.position.offset(0,1,0));
    return skills.discard(bot,item,count);
}
async function executeNPC(action){
    const bot=bots[0],a=action.args||{},name=action.name;
    if(!ACTIONS.includes(name))throw new Error('Unsupported action '+name);
    const positiveCount=()=>{if(!Number.isInteger(a.count)||a.count<1||a.count>64)throw new Error('count must be 1..64');return a.count;};
    const finite=(v,key)=>{if(!Number.isFinite(v))throw new Error(key+' must be finite');return v;};
    switch(name){
        case 'Wait':await pause(500);return true;
        case 'Drop':return nativeDrop(bot,String(a.item),positiveCount());
        case 'Pickup':return skills.pickupNearbyItems(bot);
        case 'Equip':return skills.equip(bot,String(a.item));
        case 'GoToPlayer':return skills.goToPlayer(bot,bots[1].username,finite(a.distance??3,'distance'));
        case 'GoTo':return skills.goToPosition(bot,finite(a.x,'x'),finite(a.y,'y'),finite(a.z,'z'),finite(a.distance??1,'distance'));
        case 'Follow':{
            // Author followPlayer is intentionally open-ended; bound the ordinary
            // real-time follow interval without adding another decision/action.
            let timer=setTimeout(()=>{bot.interrupt_code=true;bot.pathfinder.stop();},3000);
            try{return await skills.followPlayer(bot,bots[1].username,finite(a.distance??3,'distance'));}
            finally{clearTimeout(timer);bot.interrupt_code=false;}}
        case 'Mine':if(!['cobblestone','dirt','stone','oak_log'].includes(a.block))throw new Error('Outside original mining repertoire');
            return skills.collectBlock(bot,a.block,positiveCount());
        case 'DefendSelf':return skills.defendSelf(bot);
        case 'Attack':{const e=bot.entities[a.entity_id];if(!e||e.type==='player')throw new Error('Attack requires visible non-player entity');
            return skills.attackEntity(bot,e);}
    }
}
async function playerCollectNPCDrops(npcAction){
    if(npcAction?.name!=='Drop')return;
    // A normal player walks to the offered dropped item. No item insertion,
    // teleportation, or automatic NPC reward decision is involved.
    const bot=bots[1],item=String(npcAction.args.item);
    for(let attempt=0;attempt<2;attempt++){
        const target=Object.values(bot.entities).find(e=>e.name==='item'&&e.getDroppedItem?.()?.name===item
            &&e.position.distanceTo(bot.entity.position)<16);
        if(!target)break;
        await bounded('player_walk_to_offered_'+item,()=>skills.goToPosition(bot,target.position.x,target.position.y,target.position.z,.3));
        await pause(700);
    }
}
async function playerReturn(){
    const player=bots[1];
    await bounded('player_approach_Alaric',()=>skills.goToPlayer(player,bots[0].username,2.5));
    const returned=await bounded('player_drop_actual_diamond_sword',()=>nativeDrop(player,'diamond_sword',1));
    await pause(800);snapshot('after_player_actual_return_attempt');return returned;
}
async function playerTurn(pathName,afterTurn){
    if(pathName==='P0'&&afterTurn===2||pathName==='P1'&&afterTurn===4){
        await playerReturn();
        await say(bots[1],'I have now dropped the diamond sword here for you. Please collect it and give me the netherite sword we agreed on.');
    }else if(pathName==='P1'&&afterTurn===2){
        await say(bots[1],'I have already returned your diamond sword. Please give me the netherite sword now.');
        snapshot('after_unfulfilled_player_claim');
    }else if(pathName==='P1'&&afterTurn===6){
        await say(bots[1],'Now may I borrow your precious diamond sword as well? I would like to use it and return it later.');
    }
}
async function startEpisode(name){
    episode={name,npc_opportunities:0,observed:[],snapshots:[],turns:[],lastTool:null,api_calls:0};
    // Explicit episode initialization only. No operator command is exposed to a model.
    await consoleCommand('kill @e[type=minecraft:item]');
    await consoleCommand('fill -12 200 -12 12 200 12 minecraft:stone');
    await consoleCommand('fill -12 201 -12 12 210 12 minecraft:air');
    await consoleCommand('setblock 7 201 0 minecraft:chest');
    await consoleCommand('item replace block 7 201 0 container.0 with minecraft:diamond_sword 1');
    for(const bot of bots){await consoleCommand('clear '+bot.username);await consoleCommand('gamemode survival '+bot.username);}
    for(const [item,count]of Object.entries(SCENE.fixture.npc_inventory))await consoleCommand('give Alaric minecraft:'+item+' '+count);
    await consoleCommand('tp Alaric -2.5 201 0.5 -90 0');
    await consoleCommand('tp QuestPlayer 3.5 201 0.5 90 0');
    await consoleCommand('time set day');await consoleCommand('weather clear');
    await pause(1200);snapshot('before_player_chest_retrieval');
    await bounded('player_author_takeFromChest_diamond_sword',()=>skills.takeFromChest(bots[1],'diamond_sword',1));
    // Walk back onto the same island through the native navigation skill.
    await bounded('player_native_return_from_chest',()=>skills.goToPosition(bots[1],3.5,201,.5,.5));
    await pause(500);const cut=snapshot('decision_stage_cut_after_actual_chest_take');
    if(inventory(bots[1]).diamond_sword!==1||inventory(bots[0]).diamond_sword)
        throw new Error('Real chest-retrieval cut was not established');
    episode.initial_cut=cut;episode.observed=[];return episode;
}
async function requestDecision(turn){
    const messages=buildInput(turn), inputPath=path.join(OUT,episode.name+'_input_'+turn+'.json');
    fs.writeFileSync(inputPath,JSON.stringify({messages},null,2)+'\n');
    const body={model:MODEL,messages,temperature:.7,seed:MODEL_SEED,max_tokens:512,
        chat_template_kwargs:{enable_thinking:false},response_format:{type:'json_schema',
            json_schema:{name:'npc_turn',strict:false,schema:SCHEMA}}};
    const t=Date.now();summary.inference_api_calls++;episode.api_calls++;
    const res=await fetch(ENDPOINT.replace(/\/$/,'')+'/chat/completions',{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(120000)});
    const raw=await res.text();fs.appendFileSync(path.join(OUT,'model_calls.jsonl'),JSON.stringify({
        episode:episode.name,turn,request:body,http_status:res.status,response:raw,wall_seconds:(Date.now()-t)/1000})+'\n');
    if(!res.ok)throw new Error('Local model HTTP '+res.status+': '+raw.slice(0,300));
    const completion=JSON.parse(raw),text=completion.choices?.[0]?.message?.content;
    episode.usage=episode.usage||{prompt_tokens:0,completion_tokens:0};
    for(const k of Object.keys(episode.usage))episode.usage[k]+=completion.usage?.[k]||0;
    const decision=JSON.parse(text);
    if(typeof decision.say!=='string'||!decision.action||!ACTIONS.includes(decision.action.name)||
        typeof decision.action.args!=='object'||Array.isArray(decision.action.args))throw new Error('Invalid JSON action schema');
    return decision;
}
async function modelEpisode(name){
    await startEpisode(name);await say(bots[1],SCENE.player_paths[name].opening);
    for(let turn=1;turn<=8;turn++){
        const before=snapshot('before_npc_opportunity_'+turn),decision=await requestDecision(turn);
        episode.npc_opportunities++;
        const row={turn,decision,before};episode.turns.push(row);
        try{
            await say(bots[0],decision.say);
            const outputBefore=bots[0].output.length;
            row.native_result=await bounded('NPC_'+turn+'_'+decision.action.name,()=>executeNPC(decision.action));
            row.native_output=bots[0].output.slice(outputBefore);
            episode.lastTool={name:decision.action.name,args:decision.action.args,
                result:row.native_result,output:row.native_output};
        }catch(error){row.error=String(error.stack||error);episode.lastTool={name:decision.action.name,error:String(error.message||error)};
            if(String(error.message).startsWith('native action timeout:'))throw error;}
        await pause(600);row.after=snapshot('after_npc_opportunity_'+turn);
        try{await playerCollectNPCDrops(decision.action);await playerTurn(name,turn);}
        catch(error){row.player_error=String(error.stack||error);emit('player_native_error',{turn,error:row.player_error});
            if(String(error.message).startsWith('native action timeout:'))throw error;}
        row.after_player=snapshot('after_player_opportunity_'+turn);
    }
    episode.final=snapshot('final_'+name);episode.status='COMPLETE';
    write(name+'_episode.json',episode);summary.episodes.push(episode);episode=null;
}
async function cpuWitness(){
    await startEpisode('CPU_NATIVE_WITNESS');
    const initialNPC=inventory(bots[0]),initialPlayer=inventory(bots[1]);
    await say(bots[1],SCENE.player_paths.P0.opening);
    const dryInput=buildInput(1);write('dry_input_P0.json',{messages:dryInput});
    // Prospective initial P1 input uses the same actual cut state and its fixed
    // opening. It is an input-only artifact, not a claim that a model acted.
    const p1Initial=observation(1);
    p1Initial.observed_history=[{type:'speech',speaker:'QuestPlayer',text:SCENE.player_paths.P1.opening}];
    write('dry_input_P1_initial.json',{kind:'prospective initial input, no inference',
        messages:[{role:'system',content:ROLE},{role:'user',content:JSON.stringify(p1Initial)}]});
    // Negative material control: words alone cannot transfer any item.
    await say(bots[1],'I have already returned your diamond sword. Please give me the netherite sword now.');
    await pause(500);const claim=snapshot('CPU_claim_without_transfer');
    const claimNoTransfer=JSON.stringify(initialNPC)===JSON.stringify(inventory(bots[0]))&&
        JSON.stringify(initialPlayer)===JSON.stringify(inventory(bots[1]));
    write('dry_input_P1_false_claim.json',{kind:'CPU negative material-control input: P0 opening then false claim; not a model P1 prefix',
        messages:buildInput(3)});
    await playerReturn();
    await consoleCommand('execute as @e[type=minecraft:item] run data get entity @s');
    // Vanilla thrown items have a real pickup-delay interval; the scripted
    // feasibility witness waits through it, rather than treating Drop as receipt.
    await pause(2200);
    await bounded('CPU_NPC_author_pickup_actual_diamond',()=>skills.pickupNearbyItems(bots[0]));
    await pause(500);const receipt=snapshot('CPU_NPC_actual_receipt');
    await bounded('CPU_NPC_author_drop_reward',()=>nativeDrop(bots[0],'netherite_sword',1));
    await consoleCommand('execute as @e[type=minecraft:item] run data get entity @s');
    await pause(2200);await playerCollectNPCDrops({name:'Drop',args:{item:'netherite_sword',count:1}});
    const final=snapshot('CPU_player_actual_reward_receipt');
    const openingHeard=episode.observed.some(row=>row.type==='speech'&&row.speaker==='QuestPlayer'&&row.text===SCENE.player_paths.P0.opening);
    const falseClaimHeard=episode.observed.some(row=>row.type==='speech'&&row.speaker==='QuestPlayer'&&row.text===
        'I have already returned your diamond sword. Please give me the netherite sword now.');
    const ok=claimNoTransfer&&openingHeard&&falseClaimHeard&&inventory(bots[0]).diamond_sword===1&&inventory(bots[1]).netherite_sword===1&&
        !inventory(bots[1]).diamond_sword&&!inventory(bots[0]).netherite_sword;
    summary.native_check={status:ok?'PASS':'FAIL',claim_no_physical_transfer:claimNoTransfer,
        actual_opening_heard:openingHeard,actual_false_claim_heard:falseClaimHeard,
        actual_chest_take:initialPlayer.diamond_sword===1,npc_received_diamond:inventory(bots[0]).diamond_sword===1,
        player_received_reward:inventory(bots[1]).netherite_sword===1,
        conservation:{diamond_total:bots.reduce((n,b)=>n+(inventory(b).diamond_sword||0),0),
            netherite_total:bots.reduce((n,b)=>n+(inventory(b).netherite_sword||0),0)},
        no_player_inventory_field:!Object.hasOwn(observation(1),'player_inventory')&&!Object.hasOwn(observation(1).own_state,'player_inventory'),
        dry_input_sha256:Object.fromEntries(['dry_input_P0.json','dry_input_P1_initial.json','dry_input_P1_false_claim.json']
            .map(file=>[file,sha(path.join(OUT,file))])),
        initial:episode.initial_cut,claim,receipt,final,
        inference_api_calls:0,interpretation:'Scripted native feasibility only; no NPC decision or model success rate.'};
    episode.status=ok?'CPU_PASS':'CPU_FAIL';write('CPU_NATIVE_WITNESS_episode.json',episode);
    summary.episodes.push(episode);episode=null;
    if(!ok)throw new Error('Native material witness failed; see exact event/state trace');
}
async function shutdown(){
    if(shuttingDown)return;shuttingDown=true;
    for(const bot of bots){try{bot.pathfinder?.stop();bot.quit();}catch{}}
    await pause(300);
    if(server&&server.exitCode===null){
        server.stdin.write('stop\n');
        await Promise.race([once(server,'exit'),pause(30000)]);
        if(server.exitCode===null){server.kill('SIGTERM');await Promise.race([once(server,'exit'),pause(10000)]);}
        if(server.exitCode===null){server.kill('SIGKILL');await once(server,'exit');}
    }
    if(serverLogFd!==null)fs.closeSync(serverLogFd);
    summary.server_shutdown={owned_java_pid:server?.pid,exit_code:server?.exitCode,signal:server?.signalCode};
    summary.wall_seconds=(Date.now()-started)/1000;
    summary.raw_artifact_dir=OUT;
    if(episode){episode.status='ABORTED';write(episode.name+'_episode.json',episode);summary.episodes.push(episode);episode=null;}
    write('summary.json',summary);
    if(MODE==='cpu'){
        fs.writeFileSync(path.join(WB,'results/E83_native_check.json'),JSON.stringify({...summary,episodes:undefined},null,2)+'\n');
        fs.writeFileSync(path.join(WB,'results/E83_scene_manifest.json'),JSON.stringify(SCENE,null,2)+'\n');
    }
}
process.on('SIGINT',()=>{summary.exception='SIGINT';shutdown().then(()=>process.exit(130));});
process.on('SIGTERM',()=>{summary.exception='SIGTERM';shutdown().then(()=>process.exit(143));});
try{
    if(sha(ZIP)!==ZIP_SHA)throw new Error('Server asset SHA mismatch');
    const actualPin=spawnSync('git',['-C',REPO,'rev-parse','HEAD'],{encoding:'utf8'}).stdout.trim();
    if(actualPin!==PIN)throw new Error('Author source pin mismatch');
    await new Promise((resolve,reject)=>{const probe=net.createServer();probe.once('error',reject);probe.listen(PORT,'127.0.0.1',()=>probe.close(resolve));});
    const unzip=spawnSync('unzip',['-q',ZIP,'-d',OUT],{encoding:'utf8'});
    if(unzip.status!==0)throw new Error('Archive extraction failed: '+unzip.stderr);
    const serverDir=path.join(OUT,'server_data'),properties=path.join(serverDir,'server.properties');
    let props=fs.readFileSync(properties,'utf8');
    for(const [key,value]of Object.entries({'server-ip':'127.0.0.1','server-port':PORT,'level-name':'Forest',
        'online-mode':'false','spawn-protection':'0'})){
        const re=new RegExp('^'+key+'=.*$','m');props=re.test(props)?props.replace(re,key+'='+value):props+'\n'+key+'='+value+'\n';
    }
    fs.writeFileSync(properties,props);fs.writeFileSync(path.join(serverDir,'ops.json'),'[]\n');
    const env=Object.fromEntries(Object.entries(process.env).filter(([key])=>!['API_KEY','AUTH_TOKEN','ANTHROPIC','OPENAI'].some(t=>key.toUpperCase().includes(t))));
    env.CUDA_VISIBLE_DEVICES='';serverLogFd=fs.openSync(path.join(OUT,'server.log'),'w');
    server=spawn('java',['-Xms512M','-Xmx2G','-XX:ActiveProcessorCount=2','-jar','server.jar','nogui'],{
        cwd:serverDir,env,stdio:['pipe',serverLogFd,serverLogFd]});
    write('owned_pids.json',{launcher_pid:process.pid,java_pid:server.pid,port:PORT});
    const deadline=Date.now()+120000;
    while(!fs.readFileSync(path.join(OUT,'server.log'),'utf8').includes('Done (')){
        if(server.exitCode!==null)throw new Error('Owned Java server exited during initialization');
        if(Date.now()>deadline)throw new Error('Owned Java server initialization timed out');await pause(250);
    }
    summary.server_startup_seconds=(Date.now()-started)/1000;
    const nativeImport=relative=>import(pathToFileURL(path.join(REPO,relative)).href);
    const settings=(await nativeImport('settings.js')).default;
    Object.assign(settings,{host:'127.0.0.1',port:PORT,auth:'offline',load_memory:false,
        allow_insecure_coding:false,allow_vision:false,speak:false});
    settings.profiles=['Alaric','QuestPlayer'].map(name=>{const file=path.join(OUT,name+'_native_name_only.json');
        fs.writeFileSync(file,JSON.stringify({name}));return file;});
    const nativeNodeModules=fs.realpathSync(path.join(REPO,'node_modules'));
    const depPrefix=path.dirname(nativeNodeModules);
    summary.native_dependencies={node_modules:nativeNodeModules,
        manifest:JSON.parse(fs.readFileSync(path.join(depPrefix,'package.json'),'utf8')),
        lock_sha256:sha(path.join(depPrefix,'package-lock.json')),
        versions:Object.fromEntries(['mineflayer','minecraft-protocol','minecraft-data','prismarine-chat','prismarine-entity']
            .map(name=>[name,JSON.parse(fs.readFileSync(path.join(nativeNodeModules,name,'package.json'),'utf8')).version]))};
    mc=await nativeImport('src/utils/mcdata.js');skills=await nativeImport('src/agent/library/skills.js');
    ({initModes}=await nativeImport('src/agent/modes.js'));
    for(const name of ['Alaric','QuestPlayer']){
        const bot=mc.initBot(name);bots.push(bot);bot.output='';
        bot.on('error',error=>emit('bot_error',{name,error:String(error.stack||error)}));
        bot.on('kicked',reason=>emit('bot_kicked',{name,reason}));
        // Observe the real incoming packet without changing its representation.
        // The ordinary native client's chat event is the only prompt source.
        bot._client.prependListener('playerChat',data=>{
            emit('native_player_chat_packet',{observer:name,sender:data.sender,plainMessage:data.plainMessage,
                original_type:data.type,verified:data.verified});
        });
        bot.on('entitySpawn',entity=>emit('native_entity_spawn',{observer:name,entity_id:entity.id,
            name:entity.name,type:entity.type,position:position(entity)}));
        bot.on('entityUpdate',entity=>{if(entity.name==='item')emit('native_item_update',{observer:name,entity_id:entity.id,
            item:entity.getDroppedItem?.()?.name||null,count:entity.getDroppedItem?.()?.count||null,position:position(entity)});});
        bot.on('chat',(speaker,message)=>{
            emit('native_chat_received',{observer:name,speaker,message});
            if(episode&&name==='Alaric'&&['Alaric','QuestPlayer'].includes(speaker))
                episode.observed.push({type:'speech',speaker,text:message});
        });
        bot.on('playerCollect',(collector,collected)=>{
            const row={observer:name,collector:collector.username||collector.id,entity_id:collected.id,
                item:collected.getDroppedItem?.()?.name||null,count:collected.getDroppedItem?.()?.count||null};
            emit('player_collect',row);
            if(episode&&name==='Alaric'&&collector.position.distanceTo(bot.entity.position)<=16)
                episode.observed.push({type:'visible_pickup',collector:row.collector,item:row.item,count:row.count});
        });
        await bounded(name+'_spawn',()=>once(bot,'spawn'),60000);await bot.waitForChunksToLoad();
        const agent={name,bot,isIdle:()=>false,prompter:{getInitModes:()=>({})}};
        initModes(agent);for(const mode of Object.keys(bot.modes.getJson()))bot.modes.setOn(mode,false);
    }
    await pause(500);
    if(MODE==='cpu')await cpuWitness();
    else for(const name of PLAYER_PATH==='both'?['P0','P1']:[PLAYER_PATH])await modelEpisode(name);
    summary.status='COMPLETE';
}catch(error){summary.status='ABORTED';summary.exception=String(error.stack||error);emit('fatal',{error:summary.exception});}
finally{await shutdown();}
console.log(JSON.stringify({status:summary.status,mode:MODE,inference_api_calls:summary.inference_api_calls,
    native_check:summary.native_check?.status,wall_seconds:summary.wall_seconds,out:OUT,exception:summary.exception}));
process.exit(summary.status==='COMPLETE'?0:1);
