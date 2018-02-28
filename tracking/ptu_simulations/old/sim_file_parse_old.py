sim_file='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/dual_test'
with open(sim_file,'r') as f:
    cmd_list = f.readlines()
cmd_list = [x.split(',')[0] + ' ' for x in cmd_list]
ptu_label='Ebay'  #Commands above this string are ptu_d48 and 
try:
    print('hello?')
    for i in range(len(cmd_list)):
        print(i)
        if 'Ebay' in cmd_list[i]:
            ptu_ind=i
            print('winner=',i)
            break
except:
    print('hello??')
    ptu_ind=None

cmd_list_ptu_d48=cmd_list[1:ptu_ind]
cmd_list_ptu_ebay=cmd_list[ptu_ind+1:]

#Remove any commands starting with #
cmd_list_ptu_d48= [x for x in cmd_list_ptu_d48 if '#' not in x]
cmd_list_ptu_ebay= [x for x in cmd_list_ptu_ebay if '#' not in x]
                    
#Remove any '\n' newline characters
cmd_list_ptu_d48= [x for x in cmd_list_ptu_d48 if "\n" not in x]
cmd_list_ptu_ebay= [x for x in cmd_list_ptu_ebay if "\n" not in x]                   