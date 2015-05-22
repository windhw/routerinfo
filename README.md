# routerinfo

##功能
不断抓取路由器信息，然后PUSH到Github上

##场景
目前这个程序跑在路由器背后的一个CubieBox(Debian系统)上,它不断把路由器的公网IP地址上传到GitHub，方便我在外网连接路由器，进而连接路由器背后的CubieBox

##系统要求
需要Python 和 git ，linux平台
##步骤

1. GitHub上新建一个空repo，并clone到本地 （假定本地路径为/path/to/repo）
2. git clone https://github.com/windhw/routerinfo.git
3. 编辑routerinfo/router.py，填入/path/to/repo 和路由器口令信息。
4. 运行python routerinfo/router.py

##附注
routerinfo里面还有一个名字叫router的shell脚本，可以放在/etc/init.d/里作为系统启动/停止脚本，当然，也可以不用。
