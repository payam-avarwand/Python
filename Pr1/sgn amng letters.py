a = input("Enter any text you want: ")
b = input("Tell me which sign or character you want to add among letters of your text: ")
s = ""; t = 0
for c1 in a:
    t+=1
for c in range(0,t):
    if c == 0 or a[c]==" " or a[c-1]==" ":
        s = s + a[c]
    else:
        s = s + b + a[c]
print(s)