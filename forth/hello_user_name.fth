variable what_name 16 allocate 
variable hello_string 7 allocate

: input_value
    10 read
    dup 0 = if 11 emit else 
    1
    then
;

: set_what_name
what_name 1 +
dup 80 ! \ P
1 + dup 114 ! \ r
1 + dup 105 ! \ i
1 + dup 110 ! \ n
1 + dup 116 ! \ t
1 + dup 32 ! \ <space>
1 + dup 121 ! \ y
1 + dup 111 ! \ o
1 + dup 117 ! \ u
1 + dup 114 ! \ r
1 + dup 32 ! \ <space>
1 + dup 110 ! \ n
1 + dup 97 ! \ a
1 + dup 109 ! \ m
1 + dup 101 ! \ e
1 + dup 10 ! \ \n
;

: set_hello 
hello_string 1 +
dup 72 ! \ H
1 + dup 101 ! \ e
1 + dup 108 ! \ l
1 + dup 108 ! \ l
1 + dup 111 ! \ o
1 + dup 44 ! \ ,
1 + dup 32 ! \ <space>
;

: print_var 
dup 0 = if 
swap 1 + dup 
@ 11 emit 
swap 1 - 
print_var
then
;

set_hello
set_what_name

what_name what_name @
print_var
hello_string hello_string @
print_var



begin input_value until


