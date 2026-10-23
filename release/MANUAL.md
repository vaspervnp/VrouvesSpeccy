# LET'S GO FOR VROUVES

*A tower defence game for the ZX Spectrum 48K and 128K*

![Title screen](img/title_en.png)

## The story

Armed with EU Directive 8647/2026, the corporate goliaths at **Frankenstein & Moreau Co.**
are deploying bio-drones, hazard squads and heavy machinery to destroy *vrouves* – the wild,
"copyrighted" mountain greens of Crete.

In the village of Zoniana the people have had enough. Deploy the defenders to protect the
Kafenio, the church, the town hall and the rest of the village, and above all their precious
sacks of bitter greens. Luckily the rebel corporate drone **Psssst** has defected, and fights
alongside the heavily fortified villagers.

## Loading the game

You need a ZX Spectrum 48K, 128K, +2 or +3 (or an emulator) and the tape `vrouves.tap` (or
`vrouves.tzx`). On a 48K type:

```
LOAD ""
```

and press ENTER; on a 128K or a +2 choose **Tape Loader** from the menu. Then press PLAY.

The loading screen shows while the game loads. On a 128K the tape goes on to the picture of
the ending, which waits in the 128K's extra memory until you win the last stage. A 48K has no
room for it: the game starts as soon as it is in, and you can stop the tape there. The ending
is the last part of the tape, and when you win the last stage the 48K asks you to press PLAY
to see it (SPACE skips it).

In an emulator, the snapshots `vrouves48.z80` and `vrouves128.z80` start the game at once
(the 128K one with the ending in it).

**Sound:** the 128K plays the music and the effects on its sound chip. The 48K plays them on
its beeper: the tune on the title screen, and in the game the effects only, since the beeper
can only sound in the time the game leaves free. M turns the tune on there too.

## The title screen

The title screen opens with a scene from the game and the main keys, then tells the story
and shows the defenders, the invaders and the high scores.

| Key | Action |
| --- | --- |
| SPACE / FIRE | Start the game |
| → (CAPS SHIFT + 8), P or joystick right | Next page |
| D | Difficulty: Medium, Hard, Hardest, Easy |
| L | Switch between English and Greek |
| M | Music on / off |

The difficulty, shown under the title, sets how many lives you get for the whole game:

| Difficulty | Lives |
| --- | --- |
| Easy | 4 |
| Medium | 3 |
| Hard | 2 |
| Hardest | none |

## The game screen

![The game screen](img/game_en.png)

* **The top bar** shows the stage and messages ("build, then press N for the wave", "wave
  cleared"). When there is nothing to say it shows the title of the game, your score and the lives
  you have left.
* **The playfield** is the village. The invaders come along the road; the drones fly their
  own way, straight over walls and trees. Your defenders go on the grass beside them.
* **The bottom bar** shows the wave (for example `03/10`), your funds (*vrouves*, the money
  of the village), the HP of the building you defend, and the seconds until the next wave
  (`NEXT`), or `GO!` while a wave is on. Below it, the selected defender with its key,
  price and what it does. When the cursor is on one of your defenders, it shows how much
  selling it would give back.

## Controls

| Key | Action |
| --- | --- |
| Cursor keys (CAPS SHIFT + 5 6 7 8) / Q A O P / Kempston joystick | Move the build cursor |
| 1 – 6 | Choose a defender (only those you have in this stage) |
| SPACE / ENTER / FIRE | Build the chosen defender on the cursor |
| S / DELETE (CAPS SHIFT + 0) | Sell the defender under the cursor |
| N | Call the next wave now |
| H | Pause / continue; BREAK (CAPS SHIFT + SPACE) while paused quits to the title screen |
| L | Switch between English and Greek, at any time |
| M | Music on / off |

A Sinclair joystick is not supported: it would press the number keys that choose the
defenders.

The cursor shows its four corners, blinking, when you can build there, and a cross when you
cannot: the cell is taken, it is not grass, or you cannot afford the defender.

## How to play

* Each stage has **ten waves**. Before the first one you have 45 seconds to build; between
  waves, 15. You start every stage with **120 vrouves** and **100 HP**.
* Every invader you stop pays you: 3 for a drone, 4 for a guard, 10 for a tank. Clearing a
  wave pays a bonus of 15 + 3 × the wave number.
* Feeling brave? Press **N** to call the next wave early: half of the seconds still left on
  the countdown are paid to you as a bonus.
* Selling a defender gives back about half its price.
* Every invader that reaches the building steals greens: a drone costs 4 HP, a guard 8, a
  tank 20. The sacks of vrouves disappear one by one as the HP drops. At 0 HP the stage is
  lost. With a life left, one life goes and you play the same stage again from the start,
  with your score as it was when the stage began. With none left, the game is over and you go
  back to the title screen.
* Survive all ten waves and you move on to the next stage. Win the last one, and the vrouves
  are safe: the whole village celebrates at a feast in front of the school. Press SPACE /
  FIRE to go back to the title screen.

## The score

Your score runs through the whole game, from stage to stage, and shows in the top bar next
to the lives you have left (`SCORE 01903 LIVES 3`) whenever the bar has no message to show:

| | Points |
| --- | --- |
| Every invader you stop | the damage it would have done: 4 for a drone, 8 for a guard, 20 for a tank |
| Every defender you build | its damage: Cretan 6, Yiayia 14, Bride 4, Psssst 5, Cauldron 8, Baker 16 (taken away again if you sell it) |
| Calling a wave early with N | every second still left on the countdown |
| A stage won | every vrouve left in your funds |

A lost stage gives no points: when you play it again with one of your lives, the score goes
back to what it was when the stage began. The game ends when you win the last stage, when you
lose a stage with no lives left, or when you quit with BREAK while paused. There is one table
for all four difficulties, so the easier levels, with more lives, make a high score easier.

When the game ends with one of the eight best scores, enter your name: three letters, UP and
DOWN to pick each one, FIRE (or RIGHT) for the next, LEFT to go back. The table lasts for as
long as the Spectrum is on.

## The defenders

Not everyone is ready from the start: the Kafenio is held by the Cretan and Psssst, and every
following stage brings one more defender to the village. A new defender is announced at the
start of its stage.

| | Key | Defender | Price | From stage | What it does |
| --- | --- | --- | --- | --- | --- |
| ![](img/cretan.png) | 1 | **Cretan** | 35 | 1 | In midnight black, with a hunting rifle. Hits drones and walkers alike. |
| ![](img/psssst.png) | 4 | **Psssst** | 80 | 1 | The defected drone. Its laser also melts armour. It hovers, so it can sit on walls, trees, graves and other blocked cells. |
| ![](img/yiayia.png) | 2 | **Yiayia** | 50 | 2 | Staff of chastisement and a pot of bitter leaves: slows down every walker near her and gives the closest a heavy bash. She cannot reach drones. |
| ![](img/bride.png) | 3 | **Bride** | 70 | 3 | Wedding white and a rapid pistol. One shot in four is a critical hit for triple damage. |
| ![](img/baker.png) | 6 | **Baker** | 60 | 4 | Hurls dakos (barley rusks) that splash onto everything around the target. |
| ![](img/cauldron.png) | 5 | **Cauldron** | 110 | 5 | A toxic cloud of "unlicensed lipids and ascorbic acids": hurts every walker around it, ignoring armour, and slows them. It cannot reach drones, and tanks dent it as they pass. |

### Neighbours

Some defenders work better side by side, and some get in each other's way. A defender right
next to its partner – left, right, above or below, not diagonally – hits harder or softer:

| Defender | next to | Damage |
| --- | --- | --- |
| Bride | a Cretan | **+50%** |
| Yiayia | a Baker | **+20%** |
| Baker | a Cretan | **–50%** |
| Psssst | a Cretan | **–20%** |

Only three defenders at a time can have a bonus. They keep it for as long as they stay next
to their partner; a fourth one gets nothing, until one of the three is sold or loses its
partner, and then the bonus passes on to the next defender waiting for one. The penalties
always count.

Before you build, the info line shows the bonus the defender would get on the cursor cell:
green for a bonus, red for a penalty. When three defenders already have a bonus, no bonus is
shown.

## The invaders

| | Invader | What it does |
| --- | --- | --- |
| ![](img/drone.png) | **Bio-drone** | Fast and fragile. Flies its own shortcut over walls and trees, so only the Cretan, Psssst, the Bride and the Baker can reach it. |
| ![](img/guard.png) | **F&M compliance guard** | Armoured, with a weed-whacker and herbicide. Armour takes some of every hit, except the Cauldron's cloud; Psssst's laser melts it away. |
| ![](img/tank.png) | **Weed destroyer** | A treaded tank with lots of armour and health. It dents Cauldrons beside the road, putting them out of action for a few seconds, and costs 20 HP if it gets through. |

The invaders get tougher with every wave. In some stages they arrive tougher still.

## The stages

<div class="stage" markdown="1">

**1. The Kafenio.** The road winds down from the hills to the village café, its porch stacked
with sacks of vrouves.

![Stage 1](img/stage1.png)

</div>

<div class="stage" markdown="1">

**2. The village church.** The greens are hidden in the church courtyard, by the priest and
the candle stand. The road is shorter, and the waves a little bigger.

![Stage 2](img/stage2.png)

</div>

<div class="stage" markdown="1">

**3. The town hall.** On the plaza under the old plane tree, by the fountain and the mayor.
The invaders here are tougher than usual.

![Stage 3](img/stage3.png)

</div>

<div class="stage" markdown="1">

**4. The bakery.** In the yard of the bakery by its wood-fired oven, among the woodpile and
the racks of drying dakos. The road crosses the map in three close lanes.

![Stage 4](img/stage4.png)

</div>

<div class="stage" markdown="1">

**5. The school.** In the schoolyard with its basketball court, the flag and the teacher.

![Stage 5](img/stage5.png)

</div>

<div class="stage" markdown="1">

**6. The village pitch.** The greens wait on the touchline by the coach and the team bench,
below stands full of villagers. The road runs around the pitch, and you can build on the
grass of the pitch itself; the drones fly straight across it.

![Stage 6](img/stage6.png)

</div>

<div class="stage" markdown="1">

**7. The cemetery church.** The last stand, at the little stone chapel among the graves and
the cypresses. The road winds between the graves, where nothing can be built – except
Psssst, who hovers.

![Stage 7](img/stage7.png)

</div>

## Tips

* Look for the bends: a defender next to two stretches of road shoots at everything twice.
* Cretans are cheap and hit everything, but a single drone wave can slip past a defence made
  of walkers-only defenders. Keep something that hits the air near the drones' route.
* Put the Yiayia where the road bends, so that the slowed walkers stay longer under fire.
* Put Brides beside Cretans, and keep Bakers and Psssst a step away from them.
* Against armoured guards and tanks, Psssst's laser and the Cauldron's cloud are worth their
  price. Keep Cauldrons a step away from the road, out of the tanks' way.
* Psssst can sit on walls, trees and graves: use the cells no one else can.
* Call waves early when your defence is comfortable: the bonus adds up.

---

*LET'S GO FOR VROUVES – REVIVE8BIT - 2026 - VASPER.*
