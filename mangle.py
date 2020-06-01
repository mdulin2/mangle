'''
GLibC Memory Protection Functions. 

These are meant to handle the pointer mangling features that were introducted into GLibC 2.32 via the research done by Checkpoint.
'''

import fire 

# Mangle the ptr
def encode_ptr(fd_ptr, storage_location):
	return (storage_location >> 12) ^ fd_ptr


# Demangle the ptr
def decode_ptr(mangled_ptr,storage_location):
	return (storage_location >> 12) ^ mangled_ptr


# Unmangle a pointer while only knowing the value of the mangled_ptr
'''
The ptr is stored in the following way: 
- (Bin Ptr) ^ (Storage Location >> 12)

Two features make this possible to predict: 
- Relative closeness to the pointers in question 
- The 12 bit shift

By using the following equation, we can determine the value 
and location of the ptr. 


Equation
==================

1. First, we KNOW the top 12 bits of the program. Because of 
the shift, the bits of the Storage Location Pointer are given 
to us for free.

2. Next, we xor this value with the next (to the right) 12 bits. 
This outputs the value of the 12 bits of the Fd Pointer.

3. Finally, if the value of the bits of the Fd Pointer and the 
Storage Location are not the same (which is possible) we can just 
subtract or add this bits back in (if not the same set of bits) on the Fd Pointer.

4. Repeat until we are at the end of the program. 
The 'known bits' are the bits outputted in step 2 for the 
next iteration.


Parameters: 
==============
value: The pointer to be demangled 
offset (optional): The difference between the storage location 
       and the stored Ptr. 
       Only required if the two pointers are greater or equal to 
       0x1000.
loc_final_bits (optional) The final twelve bits of the location 
       pointer. These are needed because the least significant 
       twelve bits are lost when shifting.

Returns: 
=============
Ptr: The pointer than is being stored 
Location: The location where the pointer is being stored.
'''
def recover_ptrs(mangled_ptr, offset=0x0, loc_final_bits=0x0):
	
	# Need to iterate in 4-bit intervals. This gets the amount of total bits that we need to act on.
	if(offset > 0):
		addition = True 
	else: 
		offset = offset * -1
		addition = False

	count = 0x0 	
	tmp_value = mangled_ptr
	while(tmp_value & 0xFFFFFF000 != 0x0):
		tmp_value = tmp_value >> 4
		count +=1 

	# Get the top-most 12 bits to initialize the process
	initial = mangled_ptr & (0xFFF * (0x10 ** count))
	final_ptr = initial
	final_location = initial
		
	known_bits = initial
	iteration = 1
	while(mangled_ptr & 0xFFFFFF00000 != 0):
		
		# Get the 12 bits to the right of the top-most 12 bits of the value.
		tmp_value = mangled_ptr & (0xFFF * (0x10 ** (count - (3 * iteration))))
		# Get the lined up 12 bits of the ptr with the offset.
		tmp_offset = offset & (0xFFF * (0x10 ** (count - (3 * iteration))))
		# Shift the values over. Then, operate on them.
		bits_shift, bits_count = __shift_to_end(known_bits)
		ptr_shift, ptr_count = __shift_to_end(tmp_value)	
		
		# Operate on the bits in order to get the ptr bits at the specific location.
		known_bits = ptr_shift ^ bits_shift
		
		# Add the new known_bits to the total for the ptr.	
		new_bits = (known_bits << (ptr_count * 4))
	
		print "New Bits: ", hex(new_bits)	
		print "Offset: ", hex(tmp_offset)
		# The 'known_bits' are the location in which the ptr was stored at that we are getting.
		final_ptr = final_ptr + new_bits

		if(addition == True):
			final_location = final_location + new_bits + tmp_offset
			known_bits = __shift_to_end(new_bits + tmp_offset)[0]
			
		else: 
			final_location = final_location + new_bits - tmp_offset
			known_bits = __shift_to_end(new_bits - tmp_offset)[0]

		print "Bits Final: ", hex(known_bits)
		# Remove the top-most three bits that were just operated on form the value.
		mangled_ptr = __remove_first_three_bytes(mangled_ptr, ptr_count + 3)

		iteration += 1

	# The least significant twelve bits are unknown for the storage location. So, we remove them.
	final_location =  final_location & 0xFFFFFFFFFFFFF000
	
	# If the final bits of the location are given, we add them back in.
	if(loc_final_bits):
		final_location += (loc_final_bits & 0xFFF)
	return final_ptr, final_location

'''
Helper functions
'''
# Remove the top-most 3 bytes of an address
def __remove_first_three_bytes(value, count):
	sub_value = value & (0xFFF * (0x10 ** (count)))
	value = value - sub_value
	return value

# Shift all until we only have the 12 left-most bits in the 12 right most bits.
def __shift_to_end(value):
	count = 0
	while(value & 0xFFFFFFFFFF000 != 0):
		value = value >> 4	
		count +=1
	return value, count

# Just an example
def showcase():
	ptr = 0x987654321
	loc = 0x987654987
	print "Starting Out"
	print "=================="
	print "Pointer: ", hex(ptr) 
	print "Storage Location: ", hex(loc)

	print "\n\nMangling the Pointers"
	print "======================"
	leaked_ptr = encode_ptr(ptr, loc)
	print "Mangled Pointer: ", hex(leaked_ptr)
	print "Demangle Pointer (manually): ", hex(decode_ptr(leaked_ptr,loc))

	print "\n\nUnmangle the Pointers with Magic"
	print "=================================="
	fixed_ptr, fixed_loc = recover_ptrs(leaked_ptr, 0x0, loc & 0xFFF)
	print "Found Pointer: ", hex(ptr)
	print "Found Location: ", hex(loc)


if __name__ == "__main__":
	fire.Fire()
