sim_file='/home/pi/Desktop/git_repos/GLO/tracking/ptu_simulations/dual_test.csv'
with open(sim_file,'r') as f:
    cmd_list = f.readlines()
cmd_list = [[x.strip().split(',')[0],
             x.strip().split(',')[1]+' ',
             x.strip().split(',')[2]+' '] for x in cmd_list]
                 