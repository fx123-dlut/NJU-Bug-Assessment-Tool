import os
import configure as c


def get_findbugs_xml(release_list):
    root_folder = c.res_path+"/projs/"+c.pro_name
    if not os.path.exists(root_folder + '/findbugs_res/'):
        os.mkdir(root_folder+'/findbugs_res')
    res_path = root_folder + '/findbugs_res/xml/'
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    classes_folder = root_folder + '/unzip_repos/'
    version_list = release_list
    for i in version_list:
        now_rel_path = classes_folder+i
        # findbugs.bat -textui -progress -high -xml -output E:/projects/py/shiwanhuoji/Fx_is_pig//projs/archiva/findbugs_res/xml/archiva-2.2.5.xml E:/projects/py/shiwanhuoji/Fx_is_pig//projs/archiva/classes_repos/archiva-archiva-2.2.5
        cmdline = 'findbugs.bat -textui -progress -xml -output '\
                  +res_path+i+'.xml '\
                  +now_rel_path
        print("now run commond is : "+cmdline)
        os.system(cmdline)
    return True

def get_findbugs_data_main(release_list):
    get_findbugs_xml(release_list)


if __name__=="__main__":
    get_findbugs_data_main()