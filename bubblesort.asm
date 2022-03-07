.section .text
.global bubsort
bubsort:
    # a0 = long *list
    # a1 = size
    # t0 = swapped
    # t1 = i
1: # do loop
    addi t0, zero, 0  # swapped = false
    addi t1, zero, 1  # i = 1
2: # for loop
    bge t1, a1, 2f    # break if i >= size
    slli t3, t1, 3    # scale i by 8 (for long)
    add t3, a0, t3    # new scaled memory address
    ld  t4, -8(t3)    # load list[i-1] into t4
    ld  t5, 0(t3)     # load list[i] into t5
    ble t4, t5, 3f    # if list[i-1] < list[i], it's in position
    # if we get here, we need to swap
    addi t0, zero, 1  # swapped = true
    sd  t4, 0(t3)     # list[i] = list[i-1]
    sd  t5, -8(t3)    # list[i-1] = list[i]
3: # bottom of for loop body
    addi t1, t1, 1    # i++
    jal zero, 2b      # loop again
2: # bottom of do loop body
    bne t0, zero, 1b  # loop if swapped = true
    jalr    zero, 0(ra) # return via return address register
