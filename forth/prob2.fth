variable result 0
variable first 1
variable second 2
variable temp 0
:_start
do
@ second
! temp
+ first
! second
/ #2
* #2
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
+ #2
;