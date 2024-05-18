variable result 0
variable first 1
variable second 2
variable temp 0
variable two 2
:_start
do
@ second
! temp
+ first
! second
/ two
* two
if @=second
@+! result
@ temp
! first
@ second
if @>4000000
leave
loop
@ result
- second
+ two
;
;#TODO переделать