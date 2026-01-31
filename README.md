This project is built on the basis of cspuz library by semiexp, which is open source unper MIT license. https://github.com/semiexp/cspuz

I want to provide more examples of cspuz code for solving pencil/paper puzzles, especially those with modified or combined rules. It might be hard to code the rules into the language of cspuz library upon first sight.

The /cspuz folder contains a slightly modified version of the cspuz library (just add some utility and output function), and the other python files in the root folder are individual puzzles.


本项目基于semiexp的cspuz库（基于MIT协议开源）。https://github.com/semiexp/cspuz

我希望提供一些用cspuz库求解一些变体或组合规则纸笔谜题的例子。对我而言，刚看到这些规则时如何将它们转化成cspuz库可解的形式可能并不显然。

/cspuz文件夹包含一个略微修改过的cspuz库版本（增加了少量效用型和输出用的函数），根目录中的其他python文件各求解了一个纸笔谜题。

目前已实现的纸笔谜题列表如下：

- `unbengable_loop.py`：蚌埠回旋-CCBC15 https://archive.cipherpuzzles.com/index.html#/problem?c=ccbc15/problems/5/42
- `samsung_galaxy.py`：三星Galaxy-CCBC16
- `star_and_sudoku.py`：群星与银河-ZJUPH（只实现了第一部分：星星+杀手框数独） https://2025.zjuph.fun/puzzle/body/qun-xing-yu-yin-he
- `three_dimensional_country.py`：三维国-CCBC1314（共5道小题） https://archive.cipherpuzzles.com/index.html#/problem?c=ccbc13/problems/CCBC-14/23
- `knight_tour.py`：Rorschachs River规则23（其中的例子是原题的6*6 example，主要用于测试对于非相邻相连网格的处理，和网格相连规则在路径中切换的处理） https://brokensign.com/puzzle/2025/12/31/rorschachs-river.html
- `simplepath_order.py`：Rorschachs River规则1（其中的例子是原题的6*6 example，主要用于测试按照网格经过顺序给经过格标号的处理） https://brokensign.com/puzzle/2025/12/31/rorschachs-river.html
- `from_maze_to_lay_down.py`：这迷宫让人烦得只想躺平-P&KU2（共6个迷宫） https://pnku2.pkupuzzle.art/#/game/miyue/summer_06
