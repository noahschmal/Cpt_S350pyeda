from pyeda.inter import *
from pyeda.boolalg.bdd import BDDZERO, BDDONE

# Create bddvars
x = bddvars('x', 5)
y = bddvars('y', 5)
z = bddvars('z', 5)

# Convert integer to 5 bit binary value for assigning nodes
def convert_num_to_expr(num, bddvar):
    binary_rep = format(num, '05b')
    expr_string = ""

    for index, bit in enumerate(binary_rep):
        if index:
            expr_string += " & "
        if bit == '0':
            expr_string += "~"

        expr_string += bddvar + "[" + str(index) + "]"

    return expr_string


# Construct graph expression
def construct_graph_expr():
    graph_expr_string = ""
    for i in range(32):
            for j in range(32):
                if (i + 3) % 32 == j % 32 or (i + 8) % 32 == j % 32:
                    if graph_expr_string:
                        graph_expr_string += " | "
                    graph_expr_string += convert_num_to_expr(i, 'x') + " & " + convert_num_to_expr(j, 'y')

    return expr(graph_expr_string)

# Construct EVEN BDD
def construct_even_expr():
    # List of our given prime values
    even_list = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

    even_expr = ""
    for val in even_list:
        if even_expr:
            even_expr += " | "
        even_expr += convert_num_to_expr(val, 'y')

    return expr(even_expr)


# Construct PRIME BDD
def construct_prime_expr():
    # list of our given prime values
    prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]

    prime_expr = ""
    for val in prime_list:
        if prime_expr:
            prime_expr += " | "
        prime_expr += convert_num_to_expr(val, 'x')

    return expr(prime_expr)

# Construct RR2 BDD
def construct_RR2(R1, R2):
    RR2 = R1.compose({y[0]: z[0], y[1]: z[1], y[2]: z[2], y[3]: z[3], y[4]: z[4]}) & R2.compose({x[0]: z[0], x[1]: z[1], x[2]: z[2], x[3]: z[3], x[4]: z[4]})
    RR2 = RR2.smoothing(z)

    return RR2

# Construct RR2star
# Copied from 10/25 lecture on Fixed Point Algorithm
def construct_RR2star(RR2):
    H = RR2
    while True:
        Hp = H
        H = Hp | construct_RR2(Hp, RR2)
        if H.equivalent(Hp):
            break
    return H
    
# Testing BDDs with x and y variables
def test_bdd_both(bdd, num1, num2):
    test_expr = convert_num_to_expr(num1, 'x') + " & " + convert_num_to_expr(num2, 'y')
    test_bdd = expr2bdd(expr(test_expr))

    return (bdd & test_bdd) != BDDZERO

# Testing BDDs with one variable
def test_bdd(bdd, num1, var):
    test_expr = convert_num_to_expr(num1, var)
    test_bdd = expr2bdd(expr(test_expr))
    
    return (bdd & test_bdd) != BDDZERO

# Test StatementA
def test_StatementA(PRIME, EVEN, RR2star):
    banana = EVEN & RR2star
    apple = banana.smoothing(y)
    fish = (~PRIME) | apple
    result = ~((~fish).smoothing(x))

    return bool(result)

def main():
    # Creates an expression for the edges of Graph G
    R = construct_graph_expr()

    # Step 3.1
    # Convert the expression to a BDD
    RR = expr2bdd(R)

    # Create EVEN and PRIME BDDs
    EVEN = expr2bdd(construct_even_expr())

    PRIME = expr2bdd(construct_prime_expr())

    # RR, EVEN, and PRIME test cases
    print("RR(27,3) is " + str(test_bdd_both(RR, 27, 3)))
    print("RR(16,20) is " + str(test_bdd_both(RR, 16, 20)))
    print("EVEN(14) is " + str(test_bdd(EVEN, 14, 'y')))
    print("EVEN(13) is " + str(test_bdd(EVEN, 13, 'y')))
    print("PRIME(7) is " + str(test_bdd(PRIME, 7, 'x')))
    print("PRIME(2) is " + str(test_bdd(PRIME, 2, 'x')))

    # Step 3.2
    # Compute BDD RR2 for the set R o R
    RR2 = construct_RR2(RR, RR)

    # test RR2
    print("RR2(27,6) is " + str(test_bdd_both(RR2, 27, 6)))
    print("RR2(27,9) is " + str(test_bdd_both(RR2, 27, 9)))

    # Step 3.3
    # Compute transitive closure of RR2star
    RR2star = construct_RR2star(RR2)

    # Step 3.4
    print("Result of StatementA: " + str(test_StatementA(PRIME, EVEN, RR2star)))

# Calls main
main()