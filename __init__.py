import requests, time, cache
from pbf import PBF
from utils.RegCmd import RegCmd
from utils.cqcode import CQCode
from utils.coin import Coin

_name = "好感度系统扩展"
_version = "1.0.1"
_description = "扩展猪比自带的好感度系统，更加便利！"
_author = "xzyStudio"
_cost = 0.00

class coin(PBF):
    def __enter__(self):
        return [
            RegCmd(
                name = "绑定频道",
                usage = "绑定频道",
                permission = "anyone",
                function = "coin@bangding",
                description = "将正常QQ号与频道绑定",
                mode = "好  感  度",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "注册",
                usage = "注册",
                permission = "anyone",
                function = "coin@zhuce",
                description = "注册用户",
                mode = "好  感  度",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "投食",
                usage = "投食",
                permission = "anyone",
                function = "coin@toushi",
                description = "喂一喂小猪比",
                mode = "好  感  度",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "加好感度 ",
                usage = "加好感度 <QQ号或者@那个人>[ <要加的个数，不指定则随机数>]",
                permission = "owner",
                function = "coin@addCoinFunc",
                description = "给用户加好感度",
                mode = "好  感  度",
                hidden = 0,
                type = "command"
            )
        ]
    
    def bangding(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        if len(self.data.args) == 1:
            if gid != None:
                self.client.msg().raw('请在频道中发送“绑定频道”')
            else:
                self.client.msg().raw('[CQ:at,qq='+str(uid)+'] 请在任意地方（除频道外）发送“绑定频道 '+str(uid)+'”（不包括双引号）')
        else:
            value = self.data.args[1]
            self.mysql.commonx('UPDATE `botCoin` SET `cid`=%s WHERE `qn`=%s', (value, uid))
            self.client.msg().raw('绑定成功！')
            
            cache.refreshFromSql('userCoin')
    
    def toushi(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        cid = self.data.se.get('channel_id')
        uuid = self.data.uuid
        
        if cid != None:
            strr = 'cid'
            sql = 'UPDATE `botCoin` SET `toushi`=1 WHERE `uuid`="{0}" and `cid`="{1}"'.format(uuid, cid)
            sqlstr = "SELECT * FROM `botCoin` WHERE `uuid`='{0}' and `cid`='{1}'".format(uuid, cid)
        else:
            strr = 'qn'
            sql = 'UPDATE `botCoin` SET `toushi`=1 WHERE `uuid`="{0}" and `qn`={1}'.format(uuid, uid)
            sqlstr = "SELECT * FROM `botCoin` WHERE `uuid`='{0}' and `qn`='{1}'".format(uuid, uid)
        
        coinlist = self.mysql.selectx(sqlstr)
        
        if not coinlist:
            self.client.msg().raw('您还没有注册！\n快发送“注册”让{0}认识你吧'.format(self.data.botSettings.get('name')))
            return
        coinlist = coinlist[0]
        if coinlist.get('toushi') == 0:
            self.mysql.commonx(sql)
            self.client.msg().raw('投食成功！\n获得'+str(Coin(self.data).add())+'个好感度qwq')
        else:
            self.data.message = '不要贪心啊，你已经投过食啦！'
            self.client.msg().raw(self.data.message)
            # zhuan()
        
        cache.refreshFromSql('userCoin')
    
    def zhuce(self, sendFlag=1):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        userCoin = self.data.userCoin
        cid = self.data.se.get('channel_id')
        
        if cid == None:
            sql = 'INSERT INTO `botCoin` (`qn`, `value`, `uuid`) VALUES (%s, %s, %s)'
        else:
            if sendFlag:
                self.client.msg().raw('请不要在频道里注册！')
            return False
        
        if userCoin == -1:
            self.mysql.commonx(sql, (uid, self.data.botSettings.get("defaultCoin"), self.data.uuid))
            self.logger.info('注册用户'+str(uid), '好  感  度')
            if gid != None and sendFlag:
                self.client.msg().raw('[CQ:face,id=54] 注册成功！')
            
            return self.data.botSettings.get('defaultCoin')
        else:
            self.client.msg().raw('{0}已经认识你了呢qwq'.format(self.data.botSettings.get('name')))
            return userCoin
        
        cache.refreshFromSql('userCoin')
            
    def addCoinFunc(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        if ' ' in message:
            message = message.split(' ')
            userid = message[0]
            num = message[1]
            if 'at' in userid:
                userid = CQCode(self.data.message).get('qq')[0]
            self.data.se['user_id'] = userid
            userCoin = self.mysql.selectx("SELECT * FROM `botCoin` WHERE `uuid` = %s and `qn` = %s", (self.data.uuid, userid))[0].get('value')
            
            self.data.userCoin = userCoin
            coin = Coin(self.data)
            
            userCoin = coin.add(num)
        else:
            userid = message
            self.data.se['user_id'] = userid
            userCoin = self.mysql.selectx("SELECT * FROM `botCoin` WHERE `uuid` = %s and `qn` = %s", (self.data.uuid, userid))[0].get('value')
            
            self.data.userCoin = userCoin
            coin = Coin(self.data)
            
            userCoin = coin.add()
        
        if userCoin == False:
            return self.client.msg().raw('用户未注册')
        self.client.msg().raw('[CQ:face,id=54] 成功给用户{0}添加{1}个好感度'.format(userid, userCoin))
        
        cache.refreshFromSql('userCoin')