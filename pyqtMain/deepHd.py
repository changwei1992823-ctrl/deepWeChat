# -*- coding: utf-8 -*-
# DeepSeek 对话模块

import os
import json
import time

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QAbstractItemView, QTableWidgetItem,
)

from common_init import *
from deepseek_client import DeepSeekClient
from dataHd import dataHandleObj
from config import config

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class deepHandle(object):
    """DeepSeek 聊天与微信消息自动回复"""

    def deepInit(self):
        dataHandleObj.readConfig("set_1")
        saved_key = self._load_deepseek_key()
        self.deep_client = DeepSeekClient(api_key=saved_key)
        self.deep_history = []
        self._deep_loading_history = False
        self._wx_auto_reply = False
        self._deep_hook_mute_until = 0
        self._deep_last_bot_reply = ""
        self.history_file = os.path.join(CUR_DIR, "chat_history.json")
        if hasattr(self, "ledt_2_deepseek_key"):
            self.ledt_2_deepseek_key.setText(saved_key or "")

        self.chat_view.setOpenExternalLinks(True)
        self.chat_view.setStyleSheet(
            "QTextBrowser { background-color:#F7F7F7; border:1px solid #CCCCCC; padding:10px; }"
        )
        self.query.installEventFilter(self)
        self.tab_1.installEventFilter(self)
        self._relayout_tab1()

        self.clear_btn.clicked.connect(self.clear_deep_history)
        if hasattr(self, "btn_2_change_deep_key"):
            self.btn_2_change_deep_key.clicked.connect(self.on_change_deepseek_key)
        self.btn_1_shoudong.clicked.connect(self.on_deep_send)
        if hasattr(self, "ckbx_2_wxHook"):
            self.ckbx_2_wxHook.stateChanged.connect(self.on_wx_hook_changed)
        if hasattr(self, "ckbx_2_hui1"):
            self.ckbx_2_hui1.stateChanged.connect(self.on_set_1_hui_changed)
        if hasattr(self, "ckbx_2_hui2"):
            self.ckbx_2_hui2.stateChanged.connect(self.on_set_1_hui_changed)
        if hasattr(self, "btn_2_shuaxin"):
            self.btn_2_shuaxin.clicked.connect(self.updateGroupList)

        self.init_ignore_list_ui()
        self._apply_set_1_checkboxes_from_config()
        self.load_deep_history()
        self._update_deep_status()

    def _load_deepseek_key(self):
        key = (config.get("set_1", {}).get("apiKey") or "").strip()
        return key or None

    def _save_deepseek_key(self, key):
        if "set_1" not in config:
            config["set_1"] = {}
        config["set_1"]["apiKey"] = key
        try:
            dataHandleObj.updateConfig("set_1", config["set_1"])
        except Exception:
            pass

    def _apply_set_1_checkboxes_from_config(self):
        """从 config[set_1] 同步 wxHook / wxHui1 / wxHui2 到设置页复选框。"""
        s1 = config.get("set_1", {})
        pairs = (
            ("ckbx_2_wxHook", "wxHook", 0),
            ("ckbx_2_hui1", "wxHui1", 1),
            ("ckbx_2_hui2", "wxHui2", 1),
        )
        for attr, key, default in pairs:
            if not hasattr(self, attr):
                continue
            w = getattr(self, attr)
            w.blockSignals(True)
            w.setChecked(int(s1.get(key, default)) == 1)
            w.blockSignals(False)
        self._wx_auto_reply = int(s1.get("wxHook", 0)) == 1

    def _save_set_1_from_checkboxes(self):
        if "set_1" not in config:
            config["set_1"] = {}
        if hasattr(self, "ckbx_2_wxHook"):
            config["set_1"]["wxHook"] = 1 if self.ckbx_2_wxHook.isChecked() else 0
        if hasattr(self, "ckbx_2_hui1"):
            config["set_1"]["wxHui1"] = 1 if self.ckbx_2_hui1.isChecked() else 0
        if hasattr(self, "ckbx_2_hui2"):
            config["set_1"]["wxHui2"] = 1 if self.ckbx_2_hui2.isChecked() else 0
        try:
            dataHandleObj.updateConfig("set_1", config["set_1"])
        except Exception:
            pass

    def on_set_1_hui_changed(self, _state=None):
        self._save_set_1_from_checkboxes()

    def _is_group_wx_message(self, json_dict, reply_wxid):
        if json_dict.get("bizchat_id"):
            return True
        if "@chatroom" in (reply_wxid or ""):
            return True
        room = (json_dict.get("room_wxid") or "").strip()
        return bool(room and "@chatroom" in room)

    def on_change_deepseek_key(self):
        key = self.ledt_2_deepseek_key.text().strip()
        if not key:
            self.lb_1_0.setText("请输入 DeepSeek API Key")
            QMessageBox.warning(self, "提示", "请输入 DeepSeek API Key", QMessageBox.Ok)
            return
        self._save_deepseek_key(key)
        self.deep_client.api_key = key
        self.lb_1_0.setText("DeepSeek Key 已保存到配置")
        QMessageBox.information(self, "提示", "API Key 已写入 config[set_1][apiKey] 并生效", QMessageBox.Ok)

    def _relayout_tab1(self):
        m = 10
        gap = 8
        btn_w = 90
        header_h = 28
        footer_h = 76
        w = self.tab_1.width()
        h = self.tab_1.height()
        if w < 200 or h < 200:
            return
        self.lb_1_fdCount.setGeometry(m, m, w - 2 * m - btn_w - gap, header_h)
        self.clear_btn.setGeometry(w - m - btn_w, m, btn_w, header_h)
        top = m + header_h + gap
        foot_top = h - m - footer_h
        self.chat_view.setGeometry(m, top, w - 2 * m, foot_top - top - gap)
        self.query.setGeometry(m, foot_top, w - 2 * m - btn_w - gap, footer_h)
        self.btn_1_shoudong.setGeometry(w - m - btn_w, foot_top + 10, btn_w, 32)

    def _make_bubble(self, sender, text):
        safe_text = text.replace("\n", "<br/>")
        if sender == "DeepSeek":
            bg, title_color, title = "#E3F2FD", "#1565C0", "DeepSeek"
        else:
            bg, title_color, title = "#DCF8C6", "#2E7D32", sender
        return (
            '<table cellspacing="0" cellpadding="0" border="0" style="margin:6px 0;">'
            '<tr><td bgcolor="' + bg + '" style="padding:10px 14px; color:#1a1a1a;">'
            '<b><font color="' + title_color + '">' + title + '</font></b><br/>'
            + safe_text +
            '</td></tr></table>'
        )

    def _update_deep_status(self):
        if self._wx_auto_reply:
            if getattr(self, "canUseWx", False):
                self.lb_1_7.setText("状态:微信自动回复中")
            else:
                self.lb_1_7.setText("状态:自动回复中(微信未连接)")
        else:
            self.lb_1_7.setText("状态:就绪")

    def _wx_display_name(self, wxid):
        if wxid in getattr(self, "wxAllDic", {}):
            return self.wxAllDic[wxid].get("nickname") or wxid
        if wxid in GM.get("AppDic", {}):
            return GM["AppDic"][wxid].get("nick_name") or wxid
        if wxid in GM.get("BackDic", {}):
            return GM["BackDic"][wxid].get("nick_name") or wxid
        return wxid

    def _parse_wx_content(self, content):
        content = content.strip()
        if ":\n" in content:
            parts = content.split(":\n", 1)
            if len(parts) == 2 and len(parts[0]) < 30:
                return parts[0], parts[1].strip()
        return None, content

    def _get_monitor_group_wxids(self):
        wxids = set()
        if hasattr(self, "getJieDanQun1"):
            jd = self.getJieDanQun1()
            if jd:
                wxids.add(jd)
        if hasattr(self, "getFdQun1"):
            fd = self.getFdQun1()
            if fd:
                wxids.add(fd)
        return wxids

    def _resolve_reply_wxid(self, json_dict):
        if json_dict.get("bizchat_id"):
            return json_dict["bizchat_id"]
        room = (json_dict.get("room_wxid") or "").strip()
        if room:
            return room
        wxid = (json_dict.get("wxid") or "").strip()
        return wxid

    def init_ignore_list_ui(self):
        if not hasattr(self, "tableWidget_2"):
            return
        self.tableWidget_2.setColumnWidth(0, 220)
        self.tableWidget_2.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget_2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget_2.verticalHeader().setVisible(False)
        dataHandleObj.readConfig("set_3")
        if "set_3" not in config or not isinstance(config["set_3"], list):
            config["set_3"] = []
        self.refresh_ignore_list()

    def refresh_ignore_list(self):
        """从 config[set_3] 刷新不理会名单表格。"""
        if not hasattr(self, "tableWidget_2"):
            return
        tab = config.get("set_3") or []
        if len(tab) > 0:
            self.tableWidget_2.setRowCount(len(tab))
            for count, tmp_str in enumerate(tab):
                self.tableWidget_2.setItem(count, 0, QTableWidgetItem(str(tmp_str)))
        else:
            self.tableWidget_2.setRowCount(0)

    def _get_ignore_list(self):
        tab = config.get("set_3") or []
        return set(str(s).strip() for s in tab if s and str(s).strip())

    def _wx_user_dic(self, wxid):
        wxid = (wxid or "").strip()
        if not wxid:
            return None
        if wxid in getattr(self, "wxMsgDic", {}):
            return self.wxMsgDic[wxid]
        if wxid in getattr(self, "wxAllDic", {}):
            d = self.wxAllDic[wxid]
            return {
                "wxid": d.get("wxid") or wxid,
                "wxcount": d.get("wxcount") or wxid,
                "nickname": d.get("nickname") or wxid,
            }
        return {"nickname": wxid, "wxcount": wxid, "wxid": wxid}

    def _match_ignore_entry(self, ignore, use_dic):
        if not ignore or not use_dic:
            return False
        for key in ("wxcount", "wxid", "nickname"):
            val = (use_dic.get(key) or "").strip()
            if val and val in ignore:
                return True
        return False

    def _is_sender_ignored(self, json_dict, nickname, reply_wxid, is_group):
        ignore = self._get_ignore_list()
        if not ignore:
            return False
        if reply_wxid in ignore:
            return True
        if nickname and nickname.strip() in ignore:
            return True
        raw_wxid = (json_dict.get("wxid") or "").strip()
        if raw_wxid in ignore:
            return True
        if raw_wxid:
            if self._match_ignore_entry(ignore, self._wx_user_dic(raw_wxid)):
                return True
        if not is_group:
            if self._match_ignore_entry(ignore, self._wx_user_dic(reply_wxid)):
                return True
        display = self._wx_display_name(raw_wxid or reply_wxid)
        if display and display in ignore:
            return True
        return False

    def on_btn_2_tianjia_clicked(self):
        if not hasattr(self, "ledt_2_wxid"):
            return
        wxid = self.ledt_2_wxid.text().strip()
        if wxid == "":
            return
        if "set_3" not in config or not isinstance(config["set_3"], list):
            config["set_3"] = []
        if wxid not in config["set_3"]:
            config["set_3"].append(wxid)
            dataHandleObj.updateConfig("set_3", config["set_3"])
            self.refresh_ignore_list()

    def on_btn_2_shanchu_clicked(self):
        if not hasattr(self, "ledt_2_wxid"):
            return
        wxid = self.ledt_2_wxid.text().strip()
        if "set_3" not in config or not isinstance(config["set_3"], list):
            config["set_3"] = []
        if wxid != "":
            if wxid in config["set_3"]:
                config["set_3"].remove(wxid)
                dataHandleObj.updateConfig("set_3", config["set_3"])
                self.refresh_ignore_list()
        elif len(config["set_3"]) != 0:
            config["set_3"].pop()
            dataHandleObj.updateConfig("set_3", config["set_3"])
            self.refresh_ignore_list()

    def _is_hook_muted(self):
        return time.time() < getattr(self, "_deep_hook_mute_until", 0)

    def _mute_wx_hook(self, seconds=4):
        self._deep_hook_mute_until = time.time() + seconds

    def _is_bot_echo(self, text):
        last = (getattr(self, "_deep_last_bot_reply", "") or "").strip()
        cur = (text or "").strip()
        if not last or not cur:
            return False
        if cur == last:
            return True
        if len(cur) >= 30 and cur in last:
            return True
        if len(last) >= 30 and last in cur:
            return True
        return False

    def _sender_label(self, json_dict, nickname, reply_wxid):
        if nickname:
            return nickname
        if str(json_dict.get("sendorrecv", "")) == "1":
            return "我"
        my = getattr(self, "myWxMsg", None) or {}
        raw_wxid = (json_dict.get("wxid") or "").strip()
        my_wxid = (my.get("wxid") or my.get("wxcount") or "").strip()
        if my_wxid and raw_wxid == my_wxid:
            return "我"
        return self._wx_display_name(reply_wxid)

    def _group_role_label(self, reply_wxid):
        jd_wxid = self.getJieDanQun1() if hasattr(self, "getJieDanQun1") else ""
        fd_wxid = self.getFdQun1() if hasattr(self, "getFdQun1") else ""
        if reply_wxid == jd_wxid:
            return "接单群"
        if reply_wxid == fd_wxid:
            return "飞单群"
        return "群聊"

    def _group_nickname(self, reply_wxid):
        name = self._wx_display_name(reply_wxid)
        if name and name != reply_wxid:
            return name
        for combo in (getattr(self, "cbx_2_1", None), getattr(self, "cbx_2_2", None)):
            if combo is None:
                continue
            text = combo.currentText().strip()
            if "|" not in text:
                continue
            nick, wxid = text.split("|", 1)
            if wxid.strip() == reply_wxid:
                return nick.strip() or reply_wxid
        return reply_wxid

    def _group_display_tag(self, reply_wxid):
        return "%s|%s" % (self._group_role_label(reply_wxid), self._group_nickname(reply_wxid))

    def _save_selected_groups(self):
        try:
            if hasattr(self, "cbx_2_1") and self.cbx_2_1.currentIndex() > -1:
                config["set_1"]["jdQun"] = self.cbx_2_1.currentText()
            if hasattr(self, "cbx_2_2") and self.cbx_2_2.currentIndex() > -1:
                config["set_1"]["fdQun"] = self.cbx_2_2.currentText()
            dataHandleObj.updateConfig("set_1", config["set_1"])
        except Exception:
            pass

    def _call_deepseek(self, query):
        try:
            items = self.deep_client.search(query)
            warning = None
            if isinstance(items, dict):
                warning = items.get("warning")
                items = items.get("results") or []

            if not items:
                response_text = "未找到结果。"
            elif isinstance(items, list):
                response_text = "\n\n".join(str(i) for i in items)
            else:
                response_text = str(items)
            if warning:
                response_text = "[警告] " + warning + "\n\n" + response_text
            return response_text
        except Exception as e:
            return "DeepSeek 调用出错：" + str(e)

    def append_deep_message(self, sender, text):
        self.deep_history.append((sender, text))
        self.chat_view.append(self._make_bubble(sender, text))
        self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())
        if not self._deep_loading_history:
            self.save_deep_history()

    def clear_deep_history(self):
        reply = QMessageBox.question(
            self,
            "确认清除",
            "是否确定要清除所有历史消息？\n此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.deep_history = []
        self.chat_view.clear()
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except Exception:
            pass

    def on_wx_hook_changed(self, state):
        enabled = state == Qt.Checked
        if enabled:
            self._save_selected_groups()
            groups = self._get_monitor_group_wxids()
            if not groups:
                if hasattr(self, "ckbx_2_wxHook"):
                    self.ckbx_2_wxHook.blockSignals(True)
                    self.ckbx_2_wxHook.setChecked(False)
                    self.ckbx_2_wxHook.blockSignals(False)
                self._wx_auto_reply = False
                self._update_deep_status()
                self.lb_1_0.setText("请先在设置页选择接单群或飞单群")
                QMessageBox.warning(
                    self, "提示",
                    "请先在「设置」页选择接单群或飞单群，并点击「刷新群列表」。",
                    QMessageBox.Ok,
                )
                self._save_set_1_from_checkboxes()
                return
            self._wx_auto_reply = True
            self.hasLogin = True
            self.lb_1_0.setText("微信 Hook 已开启，监听接单群/飞单群消息")
            if hasattr(self, "wxHdInit"):
                if not getattr(self, "canUseWx", False):
                    self.wxHdInit()
                elif hasattr(self, "updateGroupList"):
                    self.updateGroupList()
        else:
            self._wx_auto_reply = False
            self.lb_1_0.setText("微信 Hook 已关闭，群消息不自动回复")
        self._save_set_1_from_checkboxes()
        self._update_deep_status()

    def on_deep_send(self):
        if not (self.deep_client.api_key or "").strip():
            self.lb_1_0.setText("请先在设置页填写 API Key")
            return
        q = self.query.toPlainText().strip()
        if not q:
            self.lb_1_0.setText("请输入内容后再发送")
            return
        self.lb_1_0.setText("正在请求 DeepSeek...")
        self.append_deep_message("我", q)
        self.query.clear()
        QApplication.processEvents()

        response_text = self._call_deepseek(q)
        self.append_deep_message("DeepSeek", response_text)
        self.lb_1_0.setText("")

        if getattr(self, "canUseWx", False) and hasattr(self, "sendTextMsg0"):
            self.sendTextMsg0(response_text)

    def handleWxMsg(self, json_dict):
        if not self._wx_auto_reply:
            return
        if self._is_hook_muted():
            return

        msgtype = json_dict.get("msgtype")
        if msgtype not in (1, "1"):
            return

        content = json_dict.get("content", "")
        if not content or not str(content).strip():
            return

        reply_wxid = self._resolve_reply_wxid(json_dict)
        if not reply_wxid:
            return

        is_group = self._is_group_wx_message(json_dict, reply_wxid)
        if is_group:
            if int(config["set_1"].get("wxHui1", 1)) != 1:
                return
            monitor_groups = self._get_monitor_group_wxids()
            if reply_wxid not in monitor_groups:
                return
        else:
            if int(config["set_1"].get("wxHui2", 1)) != 1:
                return

        nickname, pure_content = self._parse_wx_content(str(content))
        if not pure_content:
            return
        if self._is_bot_echo(pure_content):
            return

        if self._is_sender_ignored(json_dict, nickname, reply_wxid, is_group):
            return

        sender = self._sender_label(json_dict, nickname, reply_wxid)
        group_tag = self._group_display_tag(reply_wxid)
        display_sender = "[%s] %s" % (group_tag, sender)
        self.append_deep_message(display_sender, pure_content)
        self.lb_1_0.setText("DeepSeek 正在回复 %s..." % group_tag)
        QApplication.processEvents()

        response_text = self._call_deepseek(pure_content)
        self.append_deep_message("DeepSeek", response_text)
        self.lb_1_0.setText("")

        if getattr(self, "canUseWx", False) and hasattr(self, "sendTextMsg0"):
            self._deep_last_bot_reply = response_text
            self._mute_wx_hook(5)
            self.sendTextMsg0(response_text, reply_wxid)

    def save_deep_history(self):
        try:
            data = [{"sender": s, "text": t} for s, t in self.deep_history]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_deep_history(self):
        if not os.path.exists(self.history_file):
            return
        try:
            self._deep_loading_history = True
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                sender = item.get("sender")
                text = item.get("text")
                if sender and text is not None:
                    self.deep_history.append((sender, text))
                    self.chat_view.append(self._make_bubble(sender, text))
            self.chat_view.verticalScrollBar().setValue(self.chat_view.verticalScrollBar().maximum())
        except Exception:
            pass
        finally:
            self._deep_loading_history = False

    def eventFilter(self, watched, event):
        if hasattr(self, "tab_1") and watched is self.tab_1 and event.type() == QEvent.Resize:
            self._relayout_tab1()
            return False
        if hasattr(self, "query") and watched is self.query and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.on_deep_send()
                return True
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
                self.query.insertPlainText("\n")
                return True
        return QMainWindow.eventFilter(self, watched, event)
