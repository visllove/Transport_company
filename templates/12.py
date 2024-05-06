def generator_square_polynom(a, b, c):
    def square_polynom(d):
        return a * d**2 + b * d + c

    return square_polynom

f = generator_square_polynom(a=1, b=2, c=1)
g = generator_square_polynom(a=2, b=0, c=-3)
h = generator_square_polynom(a=-3, b=-10, c=50)

print(f(3))
print(g(2))
print(h(-1))
print(input)
print(type(input))
print(f)
print(g)
print(type(f))
print(type(g))