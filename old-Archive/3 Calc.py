while 1:
    print("\nYou can select an option ... ")
    print("1 - Add\n2 - Sub\n3 - Multi\n4 - Div\n5 - Mod\n6 - Pow\n\n7 - Exit""")
    ch=int(input("-------------------------------------------------------------\n > "))
    if ch == 7:
        break
    Nr1 = int(input("Enter the first number: "))
    Nr2 = int(input("Enter the second number: "))
    if ch == 1:
        print("\n\n", Nr1+Nr2 , "\n\n")
    elif ch == 2:
        print("\n\n", Nr1-Nr2 , "\n\n")                
    elif ch == 3:
        print("\n\n", Nr1 * Nr2 , "\n\n")
    elif ch == 4:
        print("\n\n", Nr1 / Nr2 , "\n\n")
    elif ch == 5:
        print("\n\n", Nr1 % Nr2 , "\n\n")
    elif ch == 6:
        print("\n\n", Nr1 ** Nr2 , "\n\n")
    else:
        print("\n\n", "Invalid input!","\n\n")