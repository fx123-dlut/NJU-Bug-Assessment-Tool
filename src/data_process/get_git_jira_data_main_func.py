import src.collect_datas.get_data_main as gdm
import configure as c
import src.filters.filter as f
import src.tools.write_to_xls as wtx
import src.tools.compare_file as cf
import src.tools.get_commit_id as gci
import src.data_process.get_generic_bug_line as ggbl
import os


# ******主流程函数******
def main_func(rewrite = False):
    path = c.path
    res_file_path = c.res_path
    commit_id_file = res_file_path+'/res/combine.xls'
    only_bug_version_name = '1_get_only_bug_version'
    only_bug_version_path = res_file_path+'/res/'+only_bug_version_name+'.xls'
    no_anno_file_name = '1_1_no_anno_file'
    no_anno_file_path = res_file_path+'/res/'+no_anno_file_name+'.xls'
    combine_1gobv_1naf_name = '1_2_final_res'
    combine_1gobv_1naf_path = res_file_path+'/res/'+combine_1gobv_1naf_name+'.xls'

    add_del_lines_file = '2_1_add_del_lines_NoAnno_and_less4'
    add_del_lines_path = res_file_path+"res/"+add_del_lines_file+'.csv'
    generic_bug_line_file = '2_2_generic_bug_lines_with_now_version'
    generic_bug_line_path = res_file_path+"/res/"+generic_bug_line_file+'.csv'
    every_line_file_name = '2_3_from_show_every_lines'
    every_line_file_path = res_file_path+'/res/'+every_line_file_name+'.csv'
    now_last_file_name = '2_4_now_last'
    now_last_file_path = res_file_path+'/res/'+now_last_file_name+'.xls'

    # 获取初始数据
    if not os.path.exists(res_file_path+"/res/1_get_only_bug_version.xls"):
        gdm.get_data()
    # #### ############################################
    # 过滤非java文件
    file_data = wtx.get_from_xls(commit_id_file)
    # cv = f.filter_not_bug_version(file_data)
    cv = wtx.get_from_xls(only_bug_version_path)
    nmtn_changed_file,no_more_than_n = f.filter_more_than_n_version(file_data[0][0],cv,path,True,100)
    #
    # ###############################################
    # 过滤java文件中的注释
    no_anno_headers = ['commit id', 'file names', 'before', 'after']
    if rewrite or (os.path.exists(no_anno_file_path) == False):
        no_anno = f.filter_annotation(nmtn_changed_file,path)
        wtx.save_to_xls(no_anno_headers,no_anno,'test1',no_anno_file_name)

    # ############################################
    # 获取更新后符合要求的版本信息
    final_version_list = cf.combine_file1_file2(no_anno_file_path,0,6,only_bug_version_path,0,6,3,4)
    print('after filter , the final version list\'s length : '+str(len(final_version_list)))
    if rewrite or (os.path.exists(combine_1gobv_1naf_path) == False):
        wtx.save_to_xls(final_version_list[0],final_version_list[1:],'res',combine_1gobv_1naf_name)
    else:
        print("file "+combine_1gobv_1naf_name+" is already exists")
    # ################################################################
    res_no_anno = wtx.get_from_xls(combine_1gobv_1naf_path)
    commit_dict = gci.get_commit_id(commit_id_file,6,True)
    # 获取修改行
    if rewrite or (os.path.exists(add_del_lines_path) == False):
        add_del_lines = ggbl.get_del_add_line(res_no_anno,add_del_lines_file,path,commit_dict)
    else:
        print("file "+add_del_lines_file+" is already exists")
    # ##########################################################
    # 获取generic-bug-fix-line
    add_del_lines_list = wtx.get_from_csv(add_del_lines_path)
    # print(add_del_lines_list)
    if rewrite or not os.path.exists(generic_bug_line_path):
        ggbl.get_generic_bug_lines(add_del_lines_list,path,generic_bug_line_path,commit_id_file)
    else:
        print("file "+generic_bug_line_file+" is already exists")
    # generic_bug_lines = wtx.get_from_csv(generic_bug_line_path)

    # commit_dict_withoutNone = gci.get_commit_id(commit_id_file,8,False)
    commit_dict_withoutNone = gci.get_commit_id(commit_id_file,8)
    print(commit_dict_withoutNone)
    #####################################################################
    # 讲代码分开分成表格中的一行对应一个带吗行
    ggbl.split_show_to_every_lines(add_del_lines_file,every_line_file_path)
    # # #####################################################################
    # # 获取遗漏的行
    # commit_dict = gci.get_commit_id(commit_id_file,8,True)
    # cf.fix_lost_code_main(every_line_file_path,3,generic_bug_line_path,2,now_last_file_path,commit_dict,path)
    ###################################################################
    # 验证结果
    # cf.verify_res_file(add_del_lines_path,0,only_bug_version_path,0)

