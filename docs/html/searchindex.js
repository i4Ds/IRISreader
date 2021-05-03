Search.setIndex({docnames:["centroid_data","coalignment","configuration","index","installation","preprocessing","reading","sample_data","tutorial","utils"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["centroid_data.rst","coalignment.rst","configuration.rst","index.rst","installation.rst","preprocessing.rst","reading.rst","sample_data.rst","tutorial.rst","utils.rst"],objects:{"irisreader.coalignment":{find_closest_raster:[1,0,1,""],find_closest_sji:[1,0,1,""],goes_data:[1,1,1,""],hek_data:[1,1,1,""]},"irisreader.coalignment.goes_data":{get_peak_flux:[1,2,1,""],interpolate:[1,2,1,""],plot:[1,2,1,""]},"irisreader.coalignment.hek_data":{get_flares:[1,2,1,""],get_iris_coordinates:[1,2,1,""],in_fov:[1,2,1,""],plot_flares:[1,2,1,""]},"irisreader.data":{sample_observation:[7,0,1,""],sample_raster:[7,0,1,""],sample_sji:[7,0,1,""]},"irisreader.data.mg2k_centroids":{assign_mg2k_centroids:[0,0,1,""],get_mg2k_centroid_table:[0,0,1,""],get_mg2k_centroids:[0,0,1,""],interpolate:[0,0,1,""],normalize:[0,0,1,""]},"irisreader.observation":{close:[6,2,1,""]},"irisreader.preprocessing":{image_cropper:[5,1,1,""],image_cube_cropper:[5,1,1,""],spectrum_interpolator:[5,1,1,""]},"irisreader.preprocessing.image_cropper":{fit:[5,2,1,""],get_bounds:[5,2,1,""],plot_bounding_boxed:[5,2,1,""],transform:[5,2,1,""]},"irisreader.preprocessing.image_cube_cropper":{fit:[5,2,1,""],get_bounds:[5,2,1,""],get_corrupt_images:[5,2,1,""],get_null_images:[5,2,1,""]},"irisreader.preprocessing.spectrum_interpolator":{fit:[5,2,1,""],get_coordinates:[5,2,1,""],transform:[5,2,1,""]},"irisreader.raster_cube":{animate:[6,2,1,""],close:[6,2,1,""],coords2pix:[6,2,1,""],crop:[6,2,1,""],cut:[6,2,1,""],get_axis_coordinates:[6,2,1,""],get_exptimes:[6,2,1,""],get_global_raster_step:[6,2,1,""],get_goes_flux:[6,2,1,""],get_image_step:[6,2,1,""],get_interpolated_image_step:[6,2,1,""],get_nsatpix:[6,2,1,""],get_raster_pos_data:[6,2,1,""],get_raster_pos_headers:[6,2,1,""],get_raster_pos_steps:[6,2,1,""],get_timestamps:[6,2,1,""],pix2coords:[6,2,1,""],plot:[6,2,1,""],uncrop:[6,2,1,""]},"irisreader.sji_cube":{animate:[6,2,1,""],close:[6,2,1,""],coords2pix:[6,2,1,""],crop:[6,2,1,""],cut:[6,2,1,""],get_axis_coordinates:[6,2,1,""],get_exptimes:[6,2,1,""],get_global_raster_step:[6,2,1,""],get_goes_flux:[6,2,1,""],get_image_step:[6,2,1,""],get_nsatpix:[6,2,1,""],get_raster_pos_data:[6,2,1,""],get_raster_pos_headers:[6,2,1,""],get_raster_pos_steps:[6,2,1,""],get_slit_pos:[6,2,1,""],get_timestamps:[6,2,1,""],pix2coords:[6,2,1,""],plot:[6,2,1,""],uncrop:[6,2,1,""]},"irisreader.utils":{animate:[9,0,1,""],download:[9,0,1,""]},"irisreader.utils.date":{from_Tformat:[9,0,1,""],from_obsformat:[9,0,1,""],to_Tformat:[9,0,1,""],to_epoch:[9,0,1,""]},irisreader:{config_template:[2,1,1,""],get_lines:[6,0,1,""],get_obs_path:[6,0,1,""],has_line:[6,0,1,""],obs_iterator:[6,1,1,""],observation:[6,1,1,""],raster_cube:[6,1,1,""],sji_cube:[6,1,1,""]}},objnames:{"0":["py","function","Python function"],"1":["py","class","Python class"],"2":["py","method","Python method"]},objtypes:{"0":"py:function","1":"py:class","2":"py:method"},terms:{"000000e":8,"001900e":8,"004500e":8,"007200e":8,"009800e":8,"015000e":8,"054800e":8,"10064e":8,"10t00":8,"10t02":8,"10t11":8,"10t13":8,"10t14":8,"10t17":8,"10t18":8,"10t23":8,"11t00":8,"11t05":8,"14x175":8,"20140323_052543_3860263227":9,"20140329_140938_3860258481":8,"20140331_024530_3860613353":8,"20140418_123338_3820259153":8,"20140906_112339_3820259253":8,"20140910_003955_3860358888":6,"20140910_112825_3860259453":8,"20170616_030825":8,"310000e":8,"31t19":8,"3x120":8,"430600e":8,"433700e":8,"440000e":8,"443100e":8,"447300e":8,"452600e":8,"455700e":8,"458900e":8,"464100e":8,"465200e":8,"471500e":8,"475700e":8,"479900e":8,"482000e":8,"487200e":8,"490400e":8,"495600e":8,"497600e":8,"498800e":8,"501900e":8,"507100e":8,"507300e":8,"509500e":8,"511400e":8,"514500e":8,"518700e":8,"520800e":8,"527100e":8,"529600e":8,"531300e":8,"534400e":8,"536200e":8,"539700e":8,"542800e":8,"547000e":8,"547400e":8,"560800e":8,"569700e":8,"580800e":8,"583000e":8,"589700e":8,"607600e":8,"609000e":8,"612000e":8,"620900e":8,"632100e":8,"636500e":8,"63it":8,"651000e":8,"659900e":8,"673300e":8,"682200e":8,"6e4":6,"700100e":8,"709000e":8,"720400e":8,"722400e":8,"731300e":8,"744600e":8,"749100e":8,"753600e":8,"766900e":8,"775800e":8,"789200e":8,"831900e":8,"835500e":8,"861800e":8,"888000e":8,"90it":8,"914200e":8,"940500e":8,"943300e":8,"966700e":8,"992900e":8,"abstract":[2,6,8],"boolean":[1,5,6,7,9],"break":6,"case":[6,8],"class":[1,2,3,5,6,8],"default":[0,1,2,6,8,9],"final":8,"float":[0,1,5,6,9],"function":[0,1,3,5,6,8,9],"import":[0,2,4,8],"int":[0,1,2,5,6,9],"long":8,"null":[5,6,7,8],"return":[0,1,5,6,7,9],"throw":5,"true":[1,2,5,6,8,9],"try":8,"while":[5,6,8],And:2,Are:8,For:[0,2,6,8],OBS:8,Such:8,That:8,The:[0,1,2,3,5,6,8],Then:8,There:8,Used:8,Using:2,WCS:8,With:8,XRS:[1,8],a_count:8,a_flux:[1,8],a_qual_flag:8,abbrevi:[6,7],abil:1,abl:[5,6],about:[2,6],abov:[0,8],accept:6,access:[0,1,2,8],accord:6,account:[6,8],accur:8,acknowledg:8,activ:1,actual:[6,8],addit:[1,8],adjust:6,advis:[5,6],after:[5,6,8,9],again:1,aim:6,algorithm:8,align:3,all:[1,2,5,6,8,9],allow:[2,8],along:[6,8],alreadi:[1,8],also:[3,8],altern:[6,9],alwai:6,ambigu:6,angstrom:[1,6],ani:[5,6,8],anim:[3,6],anoth:8,appear:5,append:6,appli:[5,8],applic:[3,8],approach:[5,8],approxim:1,ar_noaaclass:8,ar_noaanum:8,arbitrari:[0,8],arcsec:1,arcsecond:[1,6],argmax:8,argument:8,aris:[5,6],around:[1,5,8],arrai:[0,1,5,6,8],artefact:8,assess:6,assign:0,assign_mg2k_centroid:3,assigned_centroid:0,assigned_mg2k_centroid:0,associ:[6,8],assum:6,astronom:8,astrophys:0,astropi:[6,8],attribut:[6,8],automat:[6,8,9],avail:[1,2,6,8],avoid:[6,8],axi:[0,6,8],b_count:8,b_flux:[1,8],b_qual_flag:8,bad:8,band:[5,6],bar:8,base:[2,6],basedir:6,basic:8,batch:2,becaus:[2,5,8],been:[3,6],befor:[0,8],behind:8,being:8,belong:8,below:[2,8],best:8,better:2,between:[0,1,6,8,9],big:[3,8],bin:[0,5],bit:8,black:8,bool:[0,1,2,6,9],border:[5,8],both:[0,1,6],bound:5,boundari:8,box:5,boxwarp:8,brows:8,built:8,calcul:9,call:[1,8],caller:1,camera:8,can:[1,2,5,6,8,9],care:8,caution:6,ccd:8,center:[1,5,8],centroid:3,centroids_df:0,certain:[2,5,8],chang:8,chapter:8,chdir:8,check:[5,6,8],check_coverag:[5,6],choic:8,clean:4,clear:[6,8],clip:8,clone:4,close:[6,8],closest:1,cmap:8,coalign:[2,3,6,8],coars:8,code:[2,4,8],column:[5,8],com:[2,4,8,9],combin:6,combined_rast:[1,6],come:[6,8],command:8,comment:8,common:8,comparison:6,comput:[1,2,5,8],conclud:8,config:[2,8],config_templ:3,configur:[3,8],consol:4,constrain:0,contain:[0,3,6,8],content:3,control:[6,8],conveni:8,convent:8,convert:[6,9],coordin:[1,6,8],coordinate_pair:6,coords2pix:6,corner:8,corpu:8,correct:[6,8,9],corrupt:[5,6,8],could:[5,6],count:[0,5,6,8],cours:8,coverag:[5,6],cpu:8,creat:[0,2,5,6,8,9],crop:[0,5,6,8],crop_rast:0,cube:[2,5,6,7,8,9],cubic:5,current:[2,8],cut:[5,6,8,9],cutoff_percentil:[6,8,9],dai:6,dark:8,darker:8,data:[1,2,3,4,5,6,8,9],data_cub:[6,9],data_dir:1,databas:1,datafram:[0,6],date:[1,3,6],date_ob:[6,8],date_str:9,datetim:[1,9],deal:8,debug:2,deep:8,deeper:8,default_mirror:[2,8],defin:[0,5,8],degrad:5,depend:8,desc:[6,8],descript:[5,6,8],desir:[5,7,8],determin:[5,6],develop:[2,3],deviat:5,diagnost:2,diamet:1,dict:6,dictionari:[0,6],did:8,diff:[],differ:[0,1,2,5,8,9],dimens:6,dimension:8,directli:[5,8],directori:[1,6,8,9],disabl:[5,6],discard:8,displai:[6,8,9],display_error:6,distinguish:[5,6],divid:[0,6,8],divide_by_exptim:6,divis:8,docstr:2,document:2,done:8,dot:9,down:8,downlink:8,download:[1,2,3,4,8],draw:6,drive:8,drop:8,dtype:8,due:[5,6,8],dure:[1,5,6,8],dust:8,each:[0,1,5,6,8],easi:8,easier:6,educ:8,effect:[6,9],effici:8,either:[5,6,8],els:[6,9],encod:5,end:[1,3,5,6,8],end_dat:[1,6,8],endob:8,endt:6,engin:8,entir:8,error:[5,6],error_log:6,etc:[1,6],euv:8,even:[6,8,9],event:[1,6,8],event_endtim:8,event_peaktim:8,event_starttim:8,event_typ:8,everi:[0,5],everyth:[5,6,8,9],everywher:[0,6,7],evolut:8,exampl:[0,5,6,8],expens:8,explor:8,expon:6,exposur:[6,8],exptim:8,extend:1,extens:[6,8,9],factor:2,fals:[0,1,2,5,6,7,8],familiar:8,faster:[2,6,8,9],feel:8,few:[6,8],fhnw:[2,8],fiduci:8,field:[1,8],figsiz:[6,8,9],figur:[6,8,9],file:[2,6,8,9],file_hub:2,file_object:6,filenam:6,filter:8,find:[1,6,8],find_closest_rast:3,find_closest_sji:3,first:[1,8],fit:[0,2,5,6,8,9],fits_data:8,fix:8,fl_goescl:8,fl_peakflux:8,flare:[0,1,8],flare_d:1,flare_df:8,flat:8,float32:8,flux:[1,6,8],follow:[3,8],force_valid_step:6,form:[6,8,9],format:[5,6,8,9],found:[0,5,6,8],foundat:8,four:8,fov:1,fov_margin:1,frame:[0,1,6,8,9],free:8,frm_daterun:8,frm_name:8,from:[0,1,2,3,4,5,6,8,9],from_obsformat:3,from_tformat:3,full:[2,6,8,9],full_obsid:6,full_obsid_str:9,fun:8,futur:[6,9],fuv1:8,fuv2:8,fuv:8,gamma:[6,8,9],gener:[6,8],get:[5,6,8],get_axis_coordin:6,get_bound:5,get_coordin:5,get_corrupt_imag:5,get_exptim:6,get_flar:1,get_global_raster_step:6,get_goes_flux:[6,8],get_image_step:[6,8],get_interpolated_image_step:[0,6,8],get_iris_coordin:1,get_lin:[3,8],get_mg2k_centroid:3,get_mg2k_centroid_t:3,get_nsatpix:6,get_null_imag:5,get_obs_path:3,get_peak_flux:1,get_raster_pos_data:6,get_raster_pos_head:6,get_raster_pos_step:6,get_slit_po:6,get_timestamp:[1,6],gist_heat:8,git:4,github:4,give:[1,2,8],given:[0,1,5,6,8,9],global:[4,6],goe:[1,2,6,8],goes15:[1,8],goes_base_url:[2,8],goes_data:3,goes_flux:8,going:8,good:8,gov:[2,8],govern:8,great:8,grid:6,guid:8,hack:8,had:8,half:5,handl:[8,9],happen:[5,6],hard:8,harddriv:8,has:[0,2,5,6,8],has_lin:[3,8],have:[0,1,2,3,4,6,8],header:[6,8],heavili:8,height:[5,6,9],hek:[1,2,6,8],hek_base_url:[2,8],hek_data:3,hek_url:2,heliophys:[1,8],help:[2,5,6,8],her:[2,8],here:[5,6,8],hidden:3,highest:8,histori:8,hold:6,home:9,hood:8,hope:8,host:2,hour:8,how:8,howev:[5,8],hpc_radiu:8,hpc_x:8,hpc_y:8,html:[6,9],http:[2,4,8,9],huwyl:0,i4d:4,i_start:6,i_stop:6,identifi:[0,5,8,9],ids:0,ignor:6,imag:[0,5,6,7,8,9],image_cropp:[3,6,8],image_cube_cropp:[3,8],image_step:6,immedi:9,implement:[5,6,8],imshow:8,in_fov:1,includ:[6,9],increas:[5,8],index:[6,8,9],index_start:[6,9],index_stop:[6,9],indic:[5,6,9],individu:[5,6,8,9],inf:8,inf_poly_2d:8,infinit:[6,9],info:6,inform:[2,8],inherit:8,insid:8,instal:[3,8],instanc:[0,1,2,6,9],instanti:1,instead:[6,8],instruct:8,instrument:1,integ:[5,6,9],intend:3,intens:[6,8,9],intensmax:8,intensmedian:8,intensmin:8,interact:[2,8],interfac:[1,3,8],interpol:[1,3,5,6,8],interpolated_imag:8,interv:8,interval_m:[6,9],investig:8,involv:3,ipython:[6,9],iri:[1,2,3,5,6,7,8,9],iris_data_cub:[1,5,6,8,9],iris_isp2wc:8,iris_l2_20140329_140938_3860258481_raster_t000_r00000:8,iris_l2_20140329_140938_3860258481_raster_t000_r00001:8,iris_l2_20140329_140938_3860258481_raster_t000_r00002:8,iris_l2_20140329_140938_3860258481_raster_t000_r00003:8,iris_l2_20140329_140938_3860258481_raster_t000_r00004:8,iris_l2_20140329_140938_3860258481_raster_t000_r00005:8,iris_l2_20140329_140938_3860258481_raster_t000_r00006:8,iris_l2_20140329_140938_3860258481_raster_t000_r00007:8,iris_l2_20140329_140938_3860258481_raster_t000_r00008:8,iris_l2_20140329_140938_3860258481_raster_t000_r00009:8,iris_l2_20140329_140938_3860258481_raster_t000_r00010:8,iris_l2_20140329_140938_3860258481_raster_t000_r00011:8,iris_l2_20140329_140938_3860258481_raster_t000_r00012:8,iris_l2_20140329_140938_3860258481_raster_t000_r00013:8,iris_l2_20140329_140938_3860258481_raster_t000_r00014:8,iris_l2_20140329_140938_3860258481_raster_t000_r00015:8,iris_l2_20140329_140938_3860258481_raster_t000_r00016:8,iris_l2_20140329_140938_3860258481_raster_t000_r00017:8,iris_l2_20140329_140938_3860258481_raster_t000_r00018:8,iris_l2_20140329_140938_3860258481_raster_t000_r00019:8,iris_l2_20140329_140938_3860258481_raster_t000_r00020:8,iris_l2_20140329_140938_3860258481_raster_t000_r00021:8,iris_l2_20140329_140938_3860258481_raster_t000_r00022:8,iris_l2_20140329_140938_3860258481_raster_t000_r00023:8,iris_l2_20140329_140938_3860258481_raster_t000_r00024:8,iris_l2_20140329_140938_3860258481_raster_t000_r00025:8,iris_l2_20140329_140938_3860258481_raster_t000_r00026:8,iris_l2_20140329_140938_3860258481_raster_t000_r00027:8,iris_l2_20140329_140938_3860258481_raster_t000_r00028:8,iris_l2_20140329_140938_3860258481_raster_t000_r00029:8,iris_l2_20140329_140938_3860258481_raster_t000_r00030:8,iris_l2_20140329_140938_3860258481_raster_t000_r00031:8,iris_l2_20140329_140938_3860258481_raster_t000_r00032:8,iris_l2_20140329_140938_3860258481_raster_t000_r00033:8,iris_l2_20140329_140938_3860258481_raster_t000_r00034:8,iris_l2_20140329_140938_3860258481_raster_t000_r00035:8,iris_l2_20140329_140938_3860258481_raster_t000_r00036:8,iris_l2_20140329_140938_3860258481_raster_t000_r00037:8,iris_l2_20140329_140938_3860258481_raster_t000_r00038:8,iris_l2_20140329_140938_3860258481_raster_t000_r00039:8,iris_l2_20140329_140938_3860258481_raster_t000_r00040:8,iris_l2_20140329_140938_3860258481_raster_t000_r00041:8,iris_l2_20140329_140938_3860258481_raster_t000_r00042:8,iris_l2_20140329_140938_3860258481_raster_t000_r00043:8,iris_l2_20140329_140938_3860258481_raster_t000_r00044:8,iris_l2_20140329_140938_3860258481_raster_t000_r00045:8,iris_l2_20140329_140938_3860258481_raster_t000_r00046:8,iris_l2_20140329_140938_3860258481_raster_t000_r00047:8,iris_l2_20140329_140938_3860258481_raster_t000_r00048:8,iris_l2_20140329_140938_3860258481_raster_t000_r00049:8,iris_l2_20140329_140938_3860258481_raster_t000_r00050:8,iris_l2_20140329_140938_3860258481_raster_t000_r00051:8,iris_l2_20140329_140938_3860258481_raster_t000_r00052:8,iris_l2_20140329_140938_3860258481_raster_t000_r00053:8,iris_l2_20140329_140938_3860258481_raster_t000_r00054:8,iris_l2_20140329_140938_3860258481_raster_t000_r00055:8,iris_l2_20140329_140938_3860258481_raster_t000_r00056:8,iris_l2_20140329_140938_3860258481_raster_t000_r00057:8,iris_l2_20140329_140938_3860258481_raster_t000_r00058:8,iris_l2_20140329_140938_3860258481_raster_t000_r00059:8,iris_l2_20140329_140938_3860258481_raster_t000_r00060:8,iris_l2_20140329_140938_3860258481_raster_t000_r00061:8,iris_l2_20140329_140938_3860258481_raster_t000_r00062:8,iris_l2_20140329_140938_3860258481_raster_t000_r00063:8,iris_l2_20140329_140938_3860258481_raster_t000_r00064:8,iris_l2_20140329_140938_3860258481_raster_t000_r00065:8,iris_l2_20140329_140938_3860258481_raster_t000_r00066:8,iris_l2_20140329_140938_3860258481_raster_t000_r00067:8,iris_l2_20140329_140938_3860258481_raster_t000_r00068:8,iris_l2_20140329_140938_3860258481_raster_t000_r00069:8,iris_l2_20140329_140938_3860258481_raster_t000_r00070:8,iris_l2_20140329_140938_3860258481_raster_t000_r00071:8,iris_l2_20140329_140938_3860258481_raster_t000_r00072:8,iris_l2_20140329_140938_3860258481_raster_t000_r00073:8,iris_l2_20140329_140938_3860258481_raster_t000_r00074:8,iris_l2_20140329_140938_3860258481_raster_t000_r00075:8,iris_l2_20140329_140938_3860258481_raster_t000_r00076:8,iris_l2_20140329_140938_3860258481_raster_t000_r00077:8,iris_l2_20140329_140938_3860258481_raster_t000_r00078:8,iris_l2_20140329_140938_3860258481_raster_t000_r00079:8,iris_l2_20140329_140938_3860258481_raster_t000_r00080:8,iris_l2_20140329_140938_3860258481_raster_t000_r00081:8,iris_l2_20140329_140938_3860258481_raster_t000_r00082:8,iris_l2_20140329_140938_3860258481_raster_t000_r00083:8,iris_l2_20140329_140938_3860258481_raster_t000_r00084:8,iris_l2_20140329_140938_3860258481_raster_t000_r00085:8,iris_l2_20140329_140938_3860258481_raster_t000_r00086:8,iris_l2_20140329_140938_3860258481_raster_t000_r00087:8,iris_l2_20140329_140938_3860258481_raster_t000_r00088:8,iris_l2_20140329_140938_3860258481_raster_t000_r00089:8,iris_l2_20140329_140938_3860258481_raster_t000_r00090:8,iris_l2_20140329_140938_3860258481_raster_t000_r00091:8,iris_l2_20140329_140938_3860258481_raster_t000_r00092:8,iris_l2_20140329_140938_3860258481_raster_t000_r00093:8,iris_l2_20140329_140938_3860258481_raster_t000_r00094:8,iris_l2_20140329_140938_3860258481_raster_t000_r00095:8,iris_l2_20140329_140938_3860258481_raster_t000_r00096:8,iris_l2_20140329_140938_3860258481_raster_t000_r00097:8,iris_l2_20140329_140938_3860258481_raster_t000_r00098:8,iris_l2_20140329_140938_3860258481_raster_t000_r00099:8,iris_l2_20140329_140938_3860258481_raster_t000_r00100:8,iris_l2_20140329_140938_3860258481_raster_t000_r00101:8,iris_l2_20140329_140938_3860258481_raster_t000_r00102:8,iris_l2_20140329_140938_3860258481_raster_t000_r00103:8,iris_l2_20140329_140938_3860258481_raster_t000_r00104:8,iris_l2_20140329_140938_3860258481_raster_t000_r00105:8,iris_l2_20140329_140938_3860258481_raster_t000_r00106:8,iris_l2_20140329_140938_3860258481_raster_t000_r00107:8,iris_l2_20140329_140938_3860258481_raster_t000_r00108:8,iris_l2_20140329_140938_3860258481_raster_t000_r00109:8,iris_l2_20140329_140938_3860258481_raster_t000_r00110:8,iris_l2_20140329_140938_3860258481_raster_t000_r00111:8,iris_l2_20140329_140938_3860258481_raster_t000_r00112:8,iris_l2_20140329_140938_3860258481_raster_t000_r00113:8,iris_l2_20140329_140938_3860258481_raster_t000_r00114:8,iris_l2_20140329_140938_3860258481_raster_t000_r00115:8,iris_l2_20140329_140938_3860258481_raster_t000_r00116:8,iris_l2_20140329_140938_3860258481_raster_t000_r00117:8,iris_l2_20140329_140938_3860258481_raster_t000_r00118:8,iris_l2_20140329_140938_3860258481_raster_t000_r00119:8,iris_l2_20140329_140938_3860258481_raster_t000_r00120:8,iris_l2_20140329_140938_3860258481_raster_t000_r00121:8,iris_l2_20140329_140938_3860258481_raster_t000_r00122:8,iris_l2_20140329_140938_3860258481_raster_t000_r00123:8,iris_l2_20140329_140938_3860258481_raster_t000_r00124:8,iris_l2_20140329_140938_3860258481_raster_t000_r00125:8,iris_l2_20140329_140938_3860258481_raster_t000_r00126:8,iris_l2_20140329_140938_3860258481_raster_t000_r00127:8,iris_l2_20140329_140938_3860258481_raster_t000_r00128:8,iris_l2_20140329_140938_3860258481_raster_t000_r00129:8,iris_l2_20140329_140938_3860258481_raster_t000_r00130:8,iris_l2_20140329_140938_3860258481_raster_t000_r00131:8,iris_l2_20140329_140938_3860258481_raster_t000_r00132:8,iris_l2_20140329_140938_3860258481_raster_t000_r00133:8,iris_l2_20140329_140938_3860258481_raster_t000_r00134:8,iris_l2_20140329_140938_3860258481_raster_t000_r00135:8,iris_l2_20140329_140938_3860258481_raster_t000_r00136:8,iris_l2_20140329_140938_3860258481_raster_t000_r00137:8,iris_l2_20140329_140938_3860258481_raster_t000_r00138:8,iris_l2_20140329_140938_3860258481_raster_t000_r00139:8,iris_l2_20140329_140938_3860258481_raster_t000_r00140:8,iris_l2_20140329_140938_3860258481_raster_t000_r00141:8,iris_l2_20140329_140938_3860258481_raster_t000_r00142:8,iris_l2_20140329_140938_3860258481_raster_t000_r00143:8,iris_l2_20140329_140938_3860258481_raster_t000_r00144:8,iris_l2_20140329_140938_3860258481_raster_t000_r00145:8,iris_l2_20140329_140938_3860258481_raster_t000_r00146:8,iris_l2_20140329_140938_3860258481_raster_t000_r00147:8,iris_l2_20140329_140938_3860258481_raster_t000_r00148:8,iris_l2_20140329_140938_3860258481_raster_t000_r00149:8,iris_l2_20140329_140938_3860258481_raster_t000_r00150:8,iris_l2_20140329_140938_3860258481_raster_t000_r00151:8,iris_l2_20140329_140938_3860258481_raster_t000_r00152:8,iris_l2_20140329_140938_3860258481_raster_t000_r00153:8,iris_l2_20140329_140938_3860258481_raster_t000_r00154:8,iris_l2_20140329_140938_3860258481_raster_t000_r00155:8,iris_l2_20140329_140938_3860258481_raster_t000_r00156:8,iris_l2_20140329_140938_3860258481_raster_t000_r00157:8,iris_l2_20140329_140938_3860258481_raster_t000_r00158:8,iris_l2_20140329_140938_3860258481_raster_t000_r00159:8,iris_l2_20140329_140938_3860258481_raster_t000_r00160:8,iris_l2_20140329_140938_3860258481_raster_t000_r00161:8,iris_l2_20140329_140938_3860258481_raster_t000_r00162:8,iris_l2_20140329_140938_3860258481_raster_t000_r00163:8,iris_l2_20140329_140938_3860258481_raster_t000_r00164:8,iris_l2_20140329_140938_3860258481_raster_t000_r00165:8,iris_l2_20140329_140938_3860258481_raster_t000_r00166:8,iris_l2_20140329_140938_3860258481_raster_t000_r00167:8,iris_l2_20140329_140938_3860258481_raster_t000_r00168:8,iris_l2_20140329_140938_3860258481_raster_t000_r00169:8,iris_l2_20140329_140938_3860258481_raster_t000_r00170:8,iris_l2_20140329_140938_3860258481_raster_t000_r00171:8,iris_l2_20140329_140938_3860258481_raster_t000_r00172:8,iris_l2_20140329_140938_3860258481_raster_t000_r00173:8,iris_l2_20140329_140938_3860258481_raster_t000_r00174:8,iris_l2_20140329_140938_3860258481_raster_t000_r00175:8,iris_l2_20140329_140938_3860258481_raster_t000_r00176:8,iris_l2_20140329_140938_3860258481_raster_t000_r00177:8,iris_l2_20140329_140938_3860258481_raster_t000_r00178:8,iris_l2_20140329_140938_3860258481_raster_t000_r00179:8,iris_l2_20140910_112825_3860259453_raster_t000_r00000:8,iris_l2_20140910_112825_3860259453_sji_1400_t000:8,iris_mk_pointdb:8,iris_prep:[6,8],iris_prep_geowave_roi:8,iris_timestamp:1,iris_xcenix:1,iris_ycenix:1,irisa:[2,8,9],irisread:[4,8],irisreader_tutorial_notebook:8,iter:[6,8],itn:6,its:[0,5,6],januari:1,jaw:[6,8],journal:0,jump:6,jupyt:8,just:[6,8],kb_archivd:8,keep:[6,8],keep_nul:[5,6,7,8],kei:8,kleint:0,knc:0,knowledg:1,knowledgebas:8,krucker:0,kwarg:[1,6],l12:8,label:[5,6],lambda:6,lambda_:8,lambda_max:[0,5,6,8],lambda_min:[0,5,6,8],larg:[5,6,8],larger:8,largest:2,lat:6,latest:[4,8],lazi:[1,6,8],lazy_ev:1,learn:[0,2,8],least:8,leav:8,leq:8,let:8,level2:[2,8,9],level2_compress:[2,8,9],level:[2,3,8],librari:[3,4,8],lies:6,limit:[2,8],line:[0,5,6,7,8],line_info:[6,8],line_specific_head:8,linspac:8,list:[0,1,2,5,6],listdir:8,lmsal:[2,8,9],load:[1,2,6,7,8],loader:8,locat:8,logfil:6,lon:6,longer:8,look:[5,6,8],lose:8,loss:[5,6],lost:8,lot:[3,8],low:[5,6],lower:[2,8],luckili:8,machin:[0,8],made:1,magnesium:8,mai:2,mainten:6,make:[0,1,4,5,6,8],mani:[2,5,6,8],manual:8,map:[2,8],margin:1,matplotlib:[6,8,9],max:0,max_open_fil:[2,8],maximum:[0,2,5,6,9],measur:[1,8],median:5,melchior:0,memmap:2,memori:[2,6,8],mention:5,method:[0,3,5,6,8],mg2k_centroid:3,mg_slice:8,midpoint:8,might:[1,2,5,6,8],millisecond:[6,9],min:8,minimum:[5,6],minut:[6,9],mirror:[2,8,9],misalign:8,miss:[5,6],mode:[2,4,6,8],modul:2,month:6,more:[2,5,6,8],most:[1,8],mostli:6,move:[5,8],mp4:[6,9],much:8,multipl:6,n_bin:0,n_break:[0,6,8],n_centroid:0,n_file:[6,8],n_raster:[6,8],n_raster_po:6,n_sji:[6,8],n_step:6,name:[6,7],nan:8,nbsp:8,ndarrai:[5,6],nearest:0,nearestcentroid:0,necessari:[6,8],need:8,neg:[5,6,8],neighbor:0,neighbour:0,network:8,never:8,next:[6,8],ngdc:[2,8],nice:8,noaa:[2,8],non:[3,5,6,8],none:[0,1,5,6,8,9],nonzero:5,normal:[3,6],note:8,notebook:8,notic:8,now:8,nowadai:8,number:[0,1,2,5,6,8,9],numpi:[0,1,5,6,8],nuv:8,object:[1,5,6,8,9],obs:[0,4,6,8],obs_channelid:8,obs_identifi:9,obs_iter:[3,8],obs_meanwavel:8,obs_observatori:8,obs_path:[0,6],observ:[0,1,2,3,5,7,8,9],obsid:[6,8,9],obvious:8,occur:[1,6,8],off:[6,8,9],offer:8,offset:5,often:[6,8,9],omit:8,onc:[2,6,8],one:[2,6,8],ones:8,onli:[1,2,5,6,8,9],onlin:2,open:[2,6,8,9],open_ob:[8,9],option:[1,2,8],order:[0,6,9],origin:8,oslo:9,other:[1,8],otherwis:[0,6,8,9],our:8,out:[2,5,6,8,9],outlier:5,output:[2,6,9],over:[2,6,8],overal:[5,6],own:8,pair:[6,8],panda:[1,6],pano:0,paramet:[0,1,5,6,7,8,9],part:[0,6,8],particl:8,particular:8,pass:[0,6],patch:[5,6],path:[0,6,8,9],peak:1,per:0,percentil:[6,9],perform:8,period:1,perman:8,photospher:6,physic:0,pictur:8,pix2coord:[6,8],pix:8,pixel:[5,6,8,9],pixel_coordin:[6,8],pixel_pair:6,place:[5,8],pleas:8,plot:[1,4,5,6,8,9],plot_bounding_box:5,plot_flar:1,plt:8,plu:1,point:[1,8],posit:[1,6,8],possibl:[2,6,8],postion:[6,9],practic:1,predict:0,prefer:8,preprocess:[3,8],present:[1,6,8],pretti:[6,9],previou:8,primari:[6,8],primary_head:[6,8],print:[2,8],prior:8,pro:6,probabl:8,problem:[2,6,8],problemat:[5,6],procedur:0,process:[6,8],progress:8,properli:8,provid:[0,3,8],purpos:8,pyplot:8,python3:4,python:[4,9],queri:1,question:6,quicklook:8,quickstart:[3,8],quiet:8,quit:8,quot:8,rai:[1,6,8],rais:6,ram:8,ran:8,rang:[0,5,6,9],raster:[0,1,2,6,7,8,9],raster_cub:[0,1,3,5,7,8,9],raster_fil:8,raster_imag:0,raster_load:6,raster_po:[6,9],raster_step:[1,6],rather:8,reach:2,read:[1,2,3,5,8],read_v4:6,readi:8,readm:8,reason:2,rec_num:8,recnum:8,record:1,recov:5,rectangular:[5,6],reduc:[6,9],reduceth:8,refer:3,region:[0,1,5,6,8],regular:6,reli:8,remov:[5,6],remove_bad:6,replac:8,repres:1,represent:6,request:8,requir:[1,4],research:[6,9],reshap:0,resolut:8,respect:[1,8],respons:2,restrict_to_obstim:[1,8],result:5,rid:8,right:8,rotat:8,round_pixel:6,routin:6,row:[0,1,5,8],run:[2,4,8],safer:8,safeti:5,sai:8,same:[0,2,8],sampl:3,sample_observ:[3,4],sample_rast:3,sample_sji:3,sat_rot:8,satdat:[2,8],satellit:3,satur:[6,8],save:1,save_path:[6,9],savefil:1,scale:6,sdc:[2,8,9],sdo:8,search:[1,6,8],second:[1,9],section:6,see:[2,6,8],seem:[2,8],seen:8,select:6,sem:[2,8],semi:0,semilog:8,send:8,separ:9,server1071:[2,8],server:8,set:[0,2,6,8,9],setup:4,sever:8,shape:[0,6,8],shift:8,shine:[6,9],should:[0,1,2,8],show:[1,6,8],shutdown:8,side:[5,8],similar:8,similarli:8,simpl:8,simpli:8,sinc:[1,6,9],singl:[6,8],sit:[6,8],size:[2,5,6,8,9],sji:[1,4,5,6,7,8,9],sji_cub:[1,3,5,7,8,9],sji_cube_inst:1,sji_load:6,sji_step:1,sketch:8,sklearn:0,slice:[6,8],slide:5,slit:[6,8],slit_posit:6,slow:[6,9],solar:[0,6,8],solarsoft:[2,8,9],some:[0,1,2,8],someth:8,sometim:[2,5,6,8],soon:8,sort:6,sourc:[0,1,2,5,6,7,9],space:1,spatial:8,spec:8,specif:[2,6,8],specifi:[1,6,9],spectra:[0,5,8],spectral:8,spectrograph:8,spectrum:[0,5,8],spectrum_interpol:3,spline:5,spread:1,ssw:8,stare:[6,8],start:[0,1,6,8,9],start_dat:[1,6,8],state:1,step:[0,1,5,6,8],still:[5,6],stop:[0,5,6,8,9],store:[1,6,8,9],str:[0,1,2,6,7,9],string:[1,6,8,9],stripe:5,structur:[3,6,8],studi:0,style:6,success:9,sudo:4,suitabl:6,sun:[6,8],supervis:0,suppli:[0,5,6],sure:[0,4,5,8],sweep:8,swpc:8,sys:8,system:2,tabl:6,take:[1,6,8,9],target_directori:[8,9],task:8,technik:[2,8],templat:2,test:[4,6],text:8,than:[5,6,8,9],thei:[5,8],them:[1,5,6,8],therefor:[5,6],thi:[1,2,5,6,8,9],thing:8,three:[6,8],through:[0,8],throughout:6,thrown:6,thu:[5,8],thursdai:1,tick:6,tied:8,time:[1,2,5,6,8,9],time_specific_head:[6,8],time_tag:8,timestamp:[1,6,8],to_epoch:3,to_tformat:3,took:8,tool:8,top:8,total:[2,6,8],toward:[5,8],transform:5,transmiss:[5,6],transpos:8,travers:6,treat:8,tri:8,tupl:[6,9],tutori:3,two:[6,8,9],type:[0,1,5,6,7,8,9],typic:[0,5,6],uio:[2,8,9],ullmann:0,uncompress:9,uncrop:6,under:8,unfilt:2,unfortun:8,uniform:6,uniqu:[6,7,8],unit:[5,6,8],univers:9,unix:1,until:5,updat:8,upon:[1,8],url:2,use:[2,3,6,8,9],use_memmap:[2,8],used:[0,2,6,8,9],useful:[2,9],user:[2,3,4,5,6,8],uses:[6,8],using:[0,5,8],usual:[5,6,8],util:[3,8],v20130925:8,valid:[5,6],valu:[0,1,2,5,6,8],variabl:[1,2,5,6],variou:8,vector:0,ver:8,verbos:2,verbosity_level:[2,8],veri:8,version:8,via:[2,8],view:[1,8],visibl:8,vmax:8,vol:[2,8,9],voloshynovskii:0,volum:0,wai:[0,1,5,8],wall:8,want:8,warn:[6,8],warp:8,wavelength:[0,5,6,8],wavenam:8,well:[5,8],were:[0,1,8],what:[1,2,8],when:[2,5,6],where:[0,1,6,8,9],whether:[0,1,5,6,7,8,9],which:[0,1,2,6,8,9],whole:[5,6],width:[5,6,9],window:[0,1,8],wing:8,within:1,without:[4,8],wl_solar_coordin:6,work:[5,8],world:8,wors:8,would:8,written:[6,9],www:[2,8,9],xcenix:[1,8],xii:8,xlabel:8,xmax:[5,8],xmin:[5,8],xra:8,xrs:8,ycenix:1,year:6,yet:[3,8],ylabel:8,ymax:[5,8],ymin:[5,8],you:[4,8],your:8,yyyymmdd_hhmmss_obsid:6,yyyymmdd_hhmmss_oooooooooo:9,zero:8},titles:["Centroid data","Co-alignment","Configuration","irisreader documentation","Installation","Preprocessing","Reading","Sample Data","Tutorial","Utils"],titleterms:{align:1,anim:9,assign_mg2k_centroid:0,centroid:0,coalign:1,config_templ:2,configur:2,data:[0,7],date:9,document:3,download:9,find_closest_rast:1,find_closest_sji:1,from_obsformat:9,from_tformat:9,get_lin:6,get_mg2k_centroid:0,get_mg2k_centroid_t:0,get_obs_path:6,goes_data:1,has_lin:6,hek_data:1,image_cropp:5,image_cube_cropp:5,instal:4,interpol:0,irisread:[0,1,2,3,5,6,7,9],mg2k_centroid:0,normal:0,obs_iter:6,observ:6,preprocess:5,raster_cub:6,read:6,sampl:7,sample_observ:7,sample_rast:7,sample_sji:7,sji_cub:6,spectrum_interpol:5,to_epoch:9,to_tformat:9,tutori:8,util:9}})