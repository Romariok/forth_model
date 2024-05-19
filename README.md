# Лабораторная работа №3. Эксперимент
- Кобелев Роман, P3212 
- `forth | stack | harv | mc -> hw | tick -> instr | struct | stream | port | pstr | prob2`
- Базовый вариант

# Язык программирования
По варианту нужно реализовать FORTH-подобный язык

```ebnf
<program> ::= <definition>*
<definition> ::= <word-definition> | <variable-definition> |<variable-allocation-definition> | <word>
<word-definition> ::= ":" <identifier> <body> ";"
<body> ::= <word>*
<word> ::= <number> | <operand> | <word-name> | <conditional> | <loop> | <comment>
<number> ::= <digit>+
<operand> ::= "+" 
            | "-" 
            | "*" 
            | "/" 
            | "read"
            | "emit" 
            | "@" 
            | "!" 
            | "mod" 
            | "<" 
            | ">" 
            | "="
            | "swap"
            | "over"
            | "dup"
            | "drop"

<variable-definition> ::= "VARIABLE" <word-name>
<variable-allocation-definition> ::= "VARIABLE" <word-name> <number> "ALLOCATE"
<conditional> ::= "IF" <body> "THEN" | "IF" <body> "ELSE" <body> "THEN" 
<loop> ::= "do" <body> "loop" | "begin" <body> "until"
<identifier> ::= <letter> (<letter> | <digit>)*
<comment> ::= "\" <any symbol except "\n">
```

## Команды

`+` - (n1 n2 -- n3) 

`-` - (n1 n2 -- n3)

`*` - (n1 n2 -- n3)

`/` - (n1 n2 -- n3)

`mod` - (n1 n2 -- n3)

`=` - (n1 n2 -- n3) n3 = -1 if n1 == n2 else 0

`<` - (n1 n2 -- n3) n3 = -1 if n1 < n2 else 0 

`>` - (n1 n2 -- n3) n3 = -1 if n1 > n2 else 0 

`swap` - (n1 n2 -- n2 n1)

`drop` - (n1 n2 -- n1)

`over` - (n1 n2 -- n1 n2 n1)

`read` - (n1 -- n2) - прочитать символ из порта `n1` и положить на стек

`emit` - (n1 n2 -- ) - вывести ASCII символ с кодом `n1` в порт `n2`

`!` - (n1 n2 -- ) - записывает в память по адресу `n1` занчение `n2`

`@` - (n1 -- n2) - загружает из памяти значение по адресу `n1`

Условный оператор `if` берёт значение из стек и выполняет тело только, если на стеке `не 0`




`variable <name> <value>` - Приисвоить переменной с именем `<name>` значение `<value>`

`:_start` - задание основной функции

`;` - `HLT`



`do loop` - условный оператор, напоминающий конструкцию `for` в большинтсве языков на основе `C`. специальное слово `i` помещает текущий индекс цикла в стек. Два верхних значения в стеке дают начальное значение (включительно) и конечное значение (исключая) для значения `i`. Начальное значение берется с вершины стека.

`leave` - выход из цикла

`if <expression>` - сравнивает значение регистра с указанным значением и устанавливает значение статуса

# Организация памяти

Так как у меня Гарвардская архитектура, то у меня память данных и память инструкций будут разделены

# Система команд

- Машинное слово - 16 бит
  
```yaml
instruction:
   op_code: 0
   addr: 0
```
# Control Unit

Занимается декодированием микрокоманд

Листинг микрокоманд:

```

```