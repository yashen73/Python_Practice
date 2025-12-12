import time



def test():
    stat = input("enter status : ")
    if stat == '1':
        time.sleep(5)
        print("it is 1 and lets check again")
        stat = input("enter status again : ")
        if stat == '1':
            print("this is 1 ")
        else :
            print("this is not 1 almost")
    else:
        print("this is not ")

test()