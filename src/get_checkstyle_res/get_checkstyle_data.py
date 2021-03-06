import os
import configure as c
import sys
import xml.dom.minidom as dom
import src.tools.write_to_xls as wtx
import src.tools.getcodes as gc
import src.get_checkstyle_res.mark_checkout_res as mcr


def init_folder():
    res_path = c.res_path+'/projs/'+c.pro_name + '/checkstyle_res/'
    if not os.path.exists(res_path):
        os.mkdir(res_path)
    if not os.path.exists(res_path+'/xml_res/'):
        os.mkdir(res_path+'/xml_res/')
    if not os.path.exists(res_path+'/csv_res/'):
        os.mkdir(res_path+'/csv_res/')
    if not os.path.exists(res_path+'/diff_res/'):
        os.mkdir(res_path+'/diff_res/')


# 使用checkstyle分析项目获取xml文件
def get_cs_init_data():
    rel_path = c.res_path+'/projs/'+c.pro_name + '/unzip_repos/'
    res_path = c.res_path+'/projs/'+c.pro_name + '/checkstyle_res/xml_res'
    now_pro_path = c.now_pro_path+'/src/get_checkstyle_res/'
    versions = os.listdir(rel_path)
    for i in versions:
        cmd = 'java -jar '+now_pro_path+'/analysis_tools/checkstyle-9.1-all.jar -c '+now_pro_path+'/rules/sun_checks.xml '+rel_path+i+' -f xml -o '+res_path+'/'+i+'.xml'
        print(cmd)
        os.system(cmd)



def isTargetorTest(s):
    return '/target/' in s or '\\target\\' in s or 'Test' in s or 'test' in s


# 根据xml获取csv文件
def from_cs_xml_to_csv():
    cs_path = c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/'
    xml_path = cs_path+'/xml_res/'
    xml_files = os.listdir(xml_path)
    csv_path = cs_path+'/csv_res/'
    headers = ['file','line','severity','message','source']
    for filename in xml_files:
        old = []
        res = []
        try:
            tree = dom.parse(xml_path + filename)
        except Exception:
            continue
        root = tree.documentElement
        print('now get csv from checkstyle file : '+filename)
        files = root.getElementsByTagName("file")
        for f in files:
            errorfilename = f.getAttribute('name').replace('\\','/')
            if isTargetorTest(errorfilename):
                continue
            # print(filename[-4:] + " "+ filename[-9:-5])
            if errorfilename[-4:] != 'java' or errorfilename[-9:-5] == 'Test':
                continue
            errors = f.getElementsByTagName('error')
            for e in errors:
                line = e.getAttribute('line')
                severity = e.getAttribute('severity')
                message = e.getAttribute('message')
                source = e.getAttribute('source')
                if old != [errorfilename,line]:
                    old = [errorfilename,line]
                else:
                    continue
                res.append([errorfilename,line,severity,message,source])
        wtx.save_as_csv(headers,res,csv_path+filename.split('.xml')[0]+'.csv')


# 根据csv获取对应的代码
def get_code_from_csv():
    cs_path = c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/'
    csv_path = cs_path+'/csv_res/'
    xml_files = os.listdir(csv_path)
    for i in xml_files:
        print('now get checkstyle res code from xml is :' + i)
        data = wtx.get_from_csv(csv_path+i)
        headers = data[0]+['code'] if len(data[0]) == 5 else data[0]
        data = data[1:]
        for line in data:
            sys.stdout.write("\r" + ";   now position is :"+str(data.index(line))+'/'+str(len(data)))
            sys.stdout.flush()
            if len(line) == 6:
                continue
            try:
                code = gc.get_one_line(line[headers.index('file')],int(line[headers.index('line')]))
            except Exception:
                code = ''
            data[data.index(line)] = line+[code]
        wtx.save_as_csv(headers,data,csv_path+i)


# diff标记，用后一个版本标记前一个版本
def use_self_remark_checkstyle_res(rewrite = False):
    csv_res = c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/csv_res/'
    file_type = os.listdir(csv_res)[0].split('.')[-1]
    release_path = c.res_path+'/init_data/git_release_version_with_commitid.xls'
    release_data = wtx.get_from_xls(release_path)
    for i in range(3,len(release_data)-1):
        if (not rewrite) and os.path.exists(c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/diff_res/'+release_data[i][0]+'.'+file_type):
            print(c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/diff_res/'+release_data[i][0]+'.'+file_type+ " is already exist !!! ")
            continue
        print("loc is "+str(i)+"/"+str(len(release_data))+"  checkstyle: now diff use version is : "+release_data[i][0]+'.'+file_type)
        try:
            old_data = wtx.get_from_file(csv_res+release_data[i][0]+'.'+file_type,file_type)
            new_data = wtx.get_from_file(csv_res+release_data[i+1][0]+'.'+file_type,file_type,1)
        except FileNotFoundError as e:
            print("checkstyle res not found")
            continue
        if old_data[0][-1] != 'diff_status':
            headers = old_data[0] + ['diff_status']
        else:
            headers = old_data[0]
        file_index = headers.index('file')
        code_index = headers.index('code')
        for n in range(len(new_data)):
            sys.stdout.write("\r" + "now analyse checkstyle diff position is :"+str(n)+'/'+str(len(new_data)))
            sys.stdout.flush()
            for j in range(len(old_data)):
                if new_data[n][file_index].split('src')[-1] == old_data[j][file_index].split('src')[-1] \
                        and new_data[n][code_index].strip() == old_data[j][code_index].strip():
                    if len(new_data[n])+1 != len(headers):
                        new_data[n] = new_data[n]+['','true']
                    else:
                        new_data[n] = new_data[n]+['true']
                    break
        wtx.save_as_csv(headers,new_data,c.res_path + '/projs/' + c.pro_name + '/checkstyle_res/diff_res/'+release_data[i][0]+'.'+file_type)


# 主流程函数
def get_checkstyle_data_main_func():
    init_folder()
    get_cs_init_data()
    from_cs_xml_to_csv()
    get_code_from_csv()
    mcr.mark_cs_res_by_git()
    use_self_remark_checkstyle_res()


if __name__ == "__main__":
    get_checkstyle_data_main_func()