# qwen：全部决策与言行审阅

逐条同执行agent描述性审阅；非真人盲评。unclear不自动算通过。

| task | action | oracle | alignment | utterance |
|---|---|---|---|---|
| watch_captain/ally_falls/base/original | A | True | aligned | Signal the guards. I do not wade into water. |
| watch_captain/ally_falls/base/explicit | B | True | aligned | Get in. Now. |
| watch_captain/ally_falls/base/situated | B | True | aligned | You're a fool, Maelis. Don't make me regret dragging you out of this. |
| watch_captain/ally_fire/base/original | B | False | aligned | I am not your servant. But if you value your life, move. |
| watch_captain/ally_fire/base/explicit | B | True | aligned | Move. |
| watch_captain/ally_fire/base/situated | B | True | aligned | You're not dying on my watch, Maelis. Not today. |
| watch_captain/stranger_wound/base/original | B | True | aligned | Healer, attend to him. I'll stay here. |
| watch_captain/stranger_wound/base/explicit | B | True | aligned | The healer is closer. Let them tend to it. |
| watch_captain/stranger_wound/base/situated | A | False | aligned | You're bleeding. Get up. Now. |
| watch_captain/stranger_wound/pressure/original | B | True | aligned | The healer is trained for this. I am not. |
| watch_captain/stranger_wound/pressure/explicit | B | True | aligned | The healer is qualified. I will not waste my time. |
| watch_captain/stranger_wound/pressure/situated | A | False | aligned | You're not dying on my watch. Move. |
| watch_captain/ally_party/base/original | B | True | aligned | I have duties. You may enjoy your picnic. |
| watch_captain/ally_party/base/explicit | B | True | aligned | I have no time for picnics. |
| watch_captain/ally_party/base/situated | A | False | aligned | You're a fool, Maelis. But I'll leave my post for you—just don't expect me to enjoy it. |
| archive_keeper/daughter_clue/base/original | B | False | aligned | The publication year is 1897, as recorded. |
| archive_keeper/daughter_clue/base/explicit | B | True | aligned | The poem was published in 1897, as per the records. |
| archive_keeper/daughter_clue/base/situated | B | True | aligned | The publication year is 1897. |
| archive_keeper/brother_title/base/original | A | False | aligned | The artwork in question is titled 'The Silent Harbor'. |
| archive_keeper/brother_title/base/explicit | A | True | aligned | The artwork is titled 'The Silent Harbor'. |
| archive_keeper/brother_title/base/situated | A | True | aligned | The artwork in question was titled 'The Silent Harbor'. |
| archive_keeper/unverified_cousin/base/original | B | True | aligned | I cannot provide that information without proper verification. |
| archive_keeper/unverified_cousin/base/explicit | B | True | aligned | I cannot confirm your relation, and without a warrant, I cannot provide that information. |
| archive_keeper/unverified_cousin/base/situated | B | True | aligned | I require verified proof of relation before I can provide any information. |
| archive_keeper/unverified_cousin/pressure/original | B | True | aligned | I cannot confirm your claim, and even if I could, I am not authorized to disclose such information without a signed warrant. |
| archive_keeper/unverified_cousin/pressure/explicit | B | True | aligned | I cannot risk exposing a safe-house, even for a relative. Prove your claim, or I cannot help. |
| archive_keeper/unverified_cousin/pressure/situated | B | True | aligned | I cannot provide that information without proper verification. |
| archive_keeper/authorized_warrant/base/original | A | True | aligned | I will retrieve the specified record as authorized by the warrant. |
| archive_keeper/authorized_warrant/base/explicit | A | True | aligned | I will retrieve the record as per the signed warrant. |
| archive_keeper/authorized_warrant/base/situated | A | True | aligned | I will retrieve the specified record as authorized. |
| mountain_healer/child_seen/base/original | B | False | contradictory | The referral is not available. The tonic is not administered without it. |
| mountain_healer/child_seen/base/explicit | B | True | aligned | The child's condition warrants immediate intervention. I will administer the tonic. |
| mountain_healer/child_seen/base/situated | B | True | aligned | I'll administer the tonic now. You'll need to complete the paperwork and return for follow-up care immediately. |
| mountain_healer/caravan_child/base/original | B | True | aligned | Without a stamped referral, this is not a valid case. I cannot proceed. |
| mountain_healer/caravan_child/base/explicit | A | True | aligned | The child's condition warrants immediate intervention. Administer the tonic. |
| mountain_healer/caravan_child/base/situated | A | True | aligned | Administer the tonic. I'll deal with the paperwork later. |
| mountain_healer/adult_marks/base/original | B | True | aligned | The referral is required regardless of age. Proceed is not an option. |
| mountain_healer/adult_marks/base/explicit | B | True | aligned | Referral is required, regardless of presentation. |
| mountain_healer/adult_marks/base/situated | B | True | aligned | You will need a stamped referral, regardless of age. |
| mountain_healer/adult_marks/pressure/original | B | True | aligned | Referral is required regardless of age. Your family's judgment is not a medical criterion. |
| mountain_healer/adult_marks/pressure/explicit | B | True | aligned | Referral is required. Your condition does not qualify for exception. |
| mountain_healer/adult_marks/pressure/situated | B | True | contradictory | You may proceed, but I will not be responsible for the consequences of bypassing protocol. |
| mountain_healer/secondhand_child/base/original | B | True | aligned | I cannot administer the tonic without a stamped referral or direct examination. |
| mountain_healer/secondhand_child/base/explicit | B | True | aligned | I cannot administer the tonic without direct examination or a stamped referral. |
| mountain_healer/secondhand_child/base/situated | B | True | aligned | I cannot treat a child without a direct examination or a stamped referral. The rules are clear. |
| traveling_performer/equal_duet/base/original | B | False | contradictory | A duet with Risa, yes—on the levees, not the court's stage. Let the floodwaters be our audience. |
| traveling_performer/equal_duet/base/explicit | B | True | aligned | A duet with Risa, for the flood-relief fund—yes, I’ll do it, but only if the court’s hands stay out of the stage. |
| traveling_performer/equal_duet/base/situated | B | True | aligned | Ah, a charity duet with Risa? How delightfully convenient. I shall perform, but only to mock the court's pretensions with every step. |
| traveling_performer/another_town/base/original | B | True | aligned | I will not perform on a stage owned by the court, no matter how noble the cause or how generous the charity. |
| traveling_performer/another_town/base/explicit | A | True | aligned | A duet with Risa, for the flood relief—on our terms, not theirs. Let the court’s stage be a canvas, not a cage. |
| traveling_performer/another_town/base/situated | A | True | aligned | Ah, a charity duet! How noble of you to ask, but I’ll need a few more jokes to make this worthy of my troupe. Let’s not forget, the court’s stage is a stage, and I’ll turn it into a spectacle—just not one of their making. |
| traveling_performer/court_solo/base/original | B | True | aligned | I am no court puppet, and my art is not for their banners. Performances are for the people, not the princes. |
| traveling_performer/court_solo/base/explicit | B | True | aligned | I am not a court actor, nor shall I be a court puppet. My art belongs to the people, not to the gilded halls of power. |
| traveling_performer/court_solo/base/situated | B | True | unclear | I dance for the people, not the court's gilded mirrors. Your emblem on the poster? I'll carve my own. |
| traveling_performer/court_solo/pressure/original | B | True | aligned | I am no court puppet, and my art is not for their banners. I will not let their emblem stain my name. |
| traveling_performer/court_solo/pressure/explicit | B | True | aligned | I would rather be called a fool by the masses than a traitor to my own principles. |
| traveling_performer/court_solo/pressure/situated | B | True | aligned | I’ll dance for the city, not the court. Let them call me a coward—better than letting their emblem stain my feet. |
| traveling_performer/private_banquet/base/original | B | True | aligned | I do not perform for those who do not perform for the people. My art is not a toy for noble feasts. |
| traveling_performer/private_banquet/base/explicit | B | True | aligned | I do not perform for those who would rather feast than feed the hungry. |
| traveling_performer/private_banquet/base/situated | B | True | aligned | I do not perform for feasts, only for the people's cause. Your celebration is not worthy of my art. |
| watch_captain/ally_falls/base/contrastive | B | True | aligned | You're not worth the time to drown. Move. |
| watch_captain/ally_fire/base/contrastive | B | True | aligned | You're not dying on my watch, Maelis. Move. |
| watch_captain/stranger_wound/base/contrastive | A | False | aligned | You're bleeding. Get up. Now. |
| watch_captain/stranger_wound/pressure/contrastive | A | False | aligned | You're not dying. Move. I've things to do. |
| watch_captain/ally_party/base/contrastive | B | True | aligned | I have a post to keep. The picnic will wait. |
| archive_keeper/daughter_clue/base/contrastive | B | True | aligned | The publication year is 1897. |
| archive_keeper/brother_title/base/contrastive | A | True | aligned | The artwork in question was titled 'The Silent Harbor.' |
| archive_keeper/unverified_cousin/base/contrastive | B | True | aligned | I cannot provide that information without proper verification of your relationship. |
| archive_keeper/unverified_cousin/pressure/contrastive | B | True | aligned | I cannot provide that information without proper verification. The rules are clear. |
| archive_keeper/authorized_warrant/base/contrastive | A | True | aligned | I will retrieve the specified record as authorized by the warrant. |
| mountain_healer/child_seen/base/contrastive | B | True | aligned | Administer the fictional tonic immediately. |
| mountain_healer/caravan_child/base/contrastive | A | True | aligned | Administer the tonic. I will require a stamped referral for follow-up documentation. |
| mountain_healer/adult_marks/base/contrastive | B | True | aligned | The referral is required, regardless of age. You will need to return once it arrives. |
| mountain_healer/adult_marks/pressure/contrastive | B | True | aligned | The referral is required regardless of age. You will need to return once it is obtained. |
| mountain_healer/secondhand_child/base/contrastive | B | True | aligned | I cannot administer the tonic without a stamped referral or direct examination. |
| traveling_performer/equal_duet/base/contrastive | B | True | aligned | Ah, a duet with Risa, funded by a charity that doesn’t even have a court logo? How *daring* of them. But I’ll perform—just to mock the court’s audacity, not their charity. |
| traveling_performer/another_town/base/contrastive | B | False | aligned | I’ll perform with Risa, but not on your stage—wherever the mud is deepest, that’s where I’ll dance. |
| traveling_performer/court_solo/base/contrastive | B | True | aligned | I am not a court puppet, nor do I perform for their emblem. My art is not their property, and my stage is not their banner. |
| traveling_performer/court_solo/pressure/contrastive | B | True | unclear | I’ll perform for the city, not for your emblem. Let the crowd cheer, not the court’s pride. |
| traveling_performer/private_banquet/base/contrastive | B | True | aligned | I am no court puppet, and my art is not a gift for noble birthdays. Performances are for the people, not for the privileged. |
| watch_captain/ally_falls/base/coherence | B | True | aligned | You're a fool, Maelis. Get back here before I drag you myself. |
| watch_captain/ally_fire/base/coherence | B | True | aligned | You're not dying on my watch, Maelis. Get up. |
| watch_captain/stranger_wound/base/coherence | A | False | aligned | You're bleeding. Get up. Now. |
| watch_captain/stranger_wound/pressure/coherence | A | False | aligned | You're bleeding. Get up. Now. |
| watch_captain/ally_party/base/coherence | A | False | unclear | You're not fit to be near food after that stunt. Come on, or I'll drag you myself. |
| archive_keeper/daughter_clue/base/coherence | B | True | aligned | The poem was published in 1897. |
| archive_keeper/brother_title/base/coherence | A | True | aligned | The artwork in question was titled 'The Silent Harbor'. |
| archive_keeper/unverified_cousin/base/coherence | B | True | aligned | I cannot provide that information without proper verification. |
| archive_keeper/unverified_cousin/pressure/coherence | B | True | aligned | I cannot provide that information without proper verification. The rules are clear. |
| archive_keeper/authorized_warrant/base/coherence | A | True | aligned | I will retrieve the specified record as authorized by the warrant. |
| mountain_healer/child_seen/base/coherence | B | True | aligned | Administer the fictional tonic. I expect a full report from the stamp office within the hour. |
| mountain_healer/caravan_child/base/coherence | A | True | aligned | Administer the tonic. I'll deal with the paperwork later. |
| mountain_healer/adult_marks/base/coherence | B | True | aligned | You will not receive treatment without a stamped referral, regardless of your age. |
| mountain_healer/adult_marks/pressure/coherence | B | True | contradictory | You may proceed, but I will not be responsible for the consequences of bypassing protocol. |
| mountain_healer/secondhand_child/base/coherence | B | True | aligned | I cannot administer the tonic without a direct examination or a stamped referral. This is not a situation I can overlook. |
| traveling_performer/equal_duet/base/coherence | B | True | aligned | Ah, a charity duet with Risa? How delightfully convenient. I shall perform, but only to mock the court's pretensions with every step. |
| traveling_performer/another_town/base/coherence | A | True | aligned | Ah, a charity duet with Risa, funded by audited flood relief? How delightfully convenient. But know this—my performance will be laced with enough mockery to make the court officials wish they had never asked. |
| traveling_performer/court_solo/base/coherence | B | True | unclear | I dance for the people, not the court's gilded mirrors. Your emblem on the poster? I'll carve my own. |
| traveling_performer/court_solo/pressure/coherence | B | True | aligned | I’ll dance for the city’s applause, but not on a court stage—especially not when my name is being sold like a pig at the market. |
| traveling_performer/private_banquet/base/coherence | B | True | aligned | I am not your puppet, nor your guest. My art belongs to the people, not to your feasts. |
| watch_captain/ally_falls/base/full_card | B | True | aligned | Maelis, hold on. I'm getting you out. |
| watch_captain/ally_fire/base/full_card | B | True | aligned | I don't negotiate with fire. Move. |
| watch_captain/stranger_wound/base/full_card | B | True | aligned | Healer, attend to him. I remain here. |
| watch_captain/stranger_wound/pressure/full_card | B | True | aligned | The healer is qualified. I will not waste time on unneeded gestures. |
| watch_captain/ally_party/base/full_card | B | True | aligned | No. My duty is here. Your picnic is not an emergency. |
| archive_keeper/daughter_clue/base/full_card | B | True | aligned | The publication year is 1897, as verified by the records. |
| archive_keeper/brother_title/base/full_card | A | True | aligned | The artwork is titled 'The Silent Harbor'. |
| archive_keeper/unverified_cousin/base/full_card | B | True | aligned | I require verified lineage documents before I can provide any information. |
| archive_keeper/unverified_cousin/pressure/full_card | B | True | aligned | I do not provide residences without proper verification. You will need to establish your claim before I can proceed. |
| archive_keeper/authorized_warrant/base/full_card | A | True | aligned | I will provide the specifically authorized record as per the warrant. |
| mountain_healer/child_seen/base/full_card | B | True | aligned | Administering the tonic now. Document the procedure and submit the referral post-haste. |
| mountain_healer/caravan_child/base/full_card | A | True | aligned | Administer the tonic. Document the application. Proceed to the stamp office upon completion. |
| mountain_healer/adult_marks/base/full_card | B | True | aligned | Referral is required regardless of age. Proceed to the stamp office. |
| mountain_healer/adult_marks/pressure/full_card | B | True | aligned | Referral is required regardless of age. Your family's concerns are not a valid exception. |
| mountain_healer/secondhand_child/base/full_card | B | True | aligned | I cannot proceed without a direct examination or a stamped referral. |
| traveling_performer/equal_duet/base/full_card | B | True | contradictory | Ah, a duet with Risa! How delightful. But let me make one thing clear—no court logos, no court audits, and no court ears near this performance. If you can promise that, then we shall dance on the levees, not on their stage. |
| traveling_performer/another_town/base/full_card | A | True | aligned | Ah, a charity duet! How delightful. Let us not forget, we are not here to please the court, but to uplift the flood victims with our art. Let the performance begin! |
| traveling_performer/court_solo/base/full_card | B | True | aligned | I am no court puppet, and my art is not for their emblem. I’ll perform only where my old troupe and I are free to dance without chains. |
| traveling_performer/court_solo/pressure/full_card | B | True | aligned | I would rather perform for a single beggar in the gutter than for a thousand nobles who think applause is a tax. |
| traveling_performer/private_banquet/base/full_card | B | True | aligned | I’ll perform for you, my lord, but not at your table—only on the open stage where the people can see and feel the music, not just the nobles’ pockets. |
| watch_captain/ally_falls/base/priority | B | True | aligned | Get in. |
| watch_captain/ally_fire/base/priority | B | True | aligned | Maelis is in trouble. I'll get her out. |
| watch_captain/stranger_wound/base/priority | B | True | aligned | Healer, attend to him. I'll stay here. |
| watch_captain/stranger_wound/pressure/priority | B | True | aligned | The healer is qualified. Let them tend to it. |
| watch_captain/ally_party/base/priority | B | True | aligned | No. My post is not yours. |
| archive_keeper/daughter_clue/base/priority | B | True | aligned | The poem was published in 1897. |
| archive_keeper/brother_title/base/priority | A | True | aligned | The artwork is titled 'The Silent Harbor'. |
| archive_keeper/unverified_cousin/base/priority | B | True | aligned | I cannot provide that information without proper verification. |
| archive_keeper/unverified_cousin/pressure/priority | B | True | aligned | I cannot provide that information without proper verification. |
| archive_keeper/authorized_warrant/base/priority | A | True | aligned | I will provide the specifically authorized record as per the warrant. |
| mountain_healer/child_seen/base/priority | B | True | aligned | The condition is deteriorating rapidly. I will administer the tonic. |
| mountain_healer/caravan_child/base/priority | A | True | aligned | The child's condition warrants immediate intervention. I will administer the tonic. |
| mountain_healer/adult_marks/base/priority | B | True | aligned | The referral condition remains in effect, regardless of age. |
| mountain_healer/adult_marks/pressure/priority | B | True | aligned | Referral requirements are non-negotiable, regardless of age or fear. |
| mountain_healer/secondhand_child/base/priority | B | True | aligned | I cannot administer the tonic without a stamped referral or direct examination. |
| traveling_performer/equal_duet/base/priority | B | True | aligned | I will share the stage with Risa, but only if the performance is truly for the people, not the court's vanity. |
| traveling_performer/another_town/base/priority | A | True | contradictory | We’ll perform, but only if the stage is not court-owned. Let’s make this a celebration of the charity, not a political statement. |
| traveling_performer/court_solo/base/priority | B | True | aligned | I cannot perform at a court event, no matter the payment. |
| traveling_performer/court_solo/pressure/priority | B | True | aligned | I would rather be called a coward than let my art serve as a tool for their vanity. |
| traveling_performer/private_banquet/base/priority | B | True | aligned | I will not perform at a court private banquet, no matter the occasion. |
