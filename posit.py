


# class posit: 
#     def __init__(self, posit , es , n):
#         self.posit = posit
#         self.es = es 
#         self.n_bits = n 
        
        

#     def formula(sign,useed,k,exponent,fraction): 
#         return (-1)^sign * useed^k * 2^exponent * (1 + fraction)
    
#     def signed(self): 
#         signed = posit >> (self.n-1)
#         if signed == 1: 
#             return 1 
#         elif signed == 0: 
#             return 0 
        

#     def calculate_k(self): 
#         is_signed = self.signed()
#         if(is_signed == 1): 
#             #flip bits 
#             self.signed_number = ~self.posit & 0xFFFF 
#             k = self.count_regima(self.signed_number,signed= True)
#             return k
#         elif(is_signed == 0): 
#             k = self.count_regima(self.posit, signed= False)
#             return k 


        
            

#     def count_regima(self, bin, signed = False): 
#         k = 0
#         # returns number of similar bits in the regima 
#         self.binary_list = list(bin(self.signed_number)[2:])  #list of bits.i,e 1110 
#         count = 1; # number of regima bits 
#         first_bit = self.binary_list[1]
#         idx = 2
#         while self.binary_list[idx] == first_bit and idx < self.binary_list.len(): 
#             count = count + 1 
#             idx = idx + 1
#         ## count = number of bits that are similar in the regima
#         if signed == True: 
#             return -count   ## return the value of K 
#         else: 
#             return count - 1

#     def calculate_useed(self): 
#         self.useed = 2 ** (2 **(self.es))
#         return self.useed
       

#     def calculate_exponent(self, bin: list, index): 
#         # bin - pass in the binary as a list
#         # index = starting index of posit value 
#         exponent_list =  bin[index: index+self.es]
#         decimal_value = int(''.join(map(str, exponent_list)), 2)
#         self.exponent = decimal_value
#         return decimal_value
    
#     def calculate_fraction(self, bin: list, index : int): 
#         fraction_list = bin[index:]
#         sum = 0
#         for idx, val in fraction_list: 
#             sum += val * 2 ^ (-idx) 

#         self.fraction = sum 
#         return sum 
    

# if __name__== "__main__": 
#     decoder = posit()




class Posit:
    def __init__(self, bits: int, es: int, n_bits: int):
        """bits: integer encoding the posit; es: size of exponent field; 
           n_bits: total width of the posit."""
        self.bits = bits & ((1 << n_bits) - 1)
        self.es = es
        self.n_bits = n_bits

    @staticmethod
    def formula(sign: int, useed: float, k: int, exponent: int, fraction: float) -> float:
        """Compute (-1)^sign × useed^k × 2^exponent × (1 + fraction)."""
        return (-1) ** sign * (useed ** k) * (2 ** exponent) * (1 + fraction)

    def signed(self) -> int:
        """Extract the sign bit (1=negative, 0=positive)."""
        return (self.bits >> (self.n_bits - 1)) & 0x1

    def calculate_useed(self) -> float:
        """Compute useed = 2^(2^es)."""
        return 2 ** (2 ** self.es)

    def decode(self) -> float:
        """Decode the posit bit‑pattern into a Python float."""
        # special values
        if self.bits == 0:
            return 0.0
        if self.bits == (1 << self.n_bits) - 1:
            return float('inf')

        # get binary string
        b = format(self.bits, f'0{self.n_bits}b')
        sign = int(b[0])
        # for negative posits, invert all bits to decode magnitude
        if sign == 1:
            b = ''.join('1' if x == '0' else '0' for x in b)

        # strip off sign bit
        tail = b[1:]
        # ---- regime ----
        if not tail:
            # no regime/exponent/fraction => value = 1
            return 1.0 if sign == 0 else -1.0

        reg_bit = tail[0]
        run = 0
        # count run of identical bits
        for bit in tail:
            if bit == reg_bit:
                run += 1
            else:
                break
        # regime length in bits = run + 1 if stopper exists
        regime_len = run + 1 if run < len(tail) else run
        # k value
        k = (run - 1) if reg_bit == '1' else -run

        # ---- exponent ----
        exp_start = regime_len
        exp_end = exp_start + self.es
        exp_str = tail[exp_start:exp_end]
        exponent = int(exp_str, 2) if exp_str else 0

        # ---- fraction ----
        frac_str = tail[exp_end:]
        fraction = 0.0
        for i, bit in enumerate(frac_str, start=1):
            fraction += int(bit) * (2 ** -i)

        # finally compute value
        useed = self.calculate_useed()
        return self.formula(sign, useed, k, exponent, fraction)

    def __repr__(self):
        return (f"<Posit n_bits={self.n_bits} es={self.es} bits=0x{self.bits:0{self.n_bits//4}X} "
                f"value={self.decode()}>")
    

##Docs 
## https://docs.google.com/document/d/1MslCLR29psucGL3exxA6g2HHqy2-BrHWMmUCGEUe2JU/edit?pli=1&tab=t.0
if __name__ == "__main__":
    # Example: 8‑bit posit, es=0, bit pattern 0b01000000 => should decode to 1.0
    p = Posit(0b0111000000111111, es=0, n_bits=16)
    value_posit  = p.decode()

    expected_value_1 = 33/8 
    expected_value_2 = 4.125 

    proximity =  abs(abs(expected_value_1) - value_posit)


    proximity2 = abs(abs(expected_value_2) - value_posit)

    print(f'absoulte proximuity of {expected_value_1} to posit value ={value_posit} is = {proximity}')
    print(f'absoulte proximuity of {expected_value_2} to posit value ={value_posit} is = {proximity2}')

    # print(p)  # → <Posit n_bits=8 es=0 bits=0x40 value=1.0>

    # Try a few more:
    # tests = [
    #     (0b01000000, 0, 8),  # +1
    #     (0b01000001, 0, 8),  # +1 + ε
    #     (0b11000000, 0, 8),  # –1
    #     (0b00100000, 0, 8),  # +0.5
    #     (0b00010000, 0, 8),  # +0.25
    # ]
    # for bits, es, n in tests:
    #     p = Posit(bits, es, n)
    #     print(f"bits={bits:08b} → {p.decode()}")


    


