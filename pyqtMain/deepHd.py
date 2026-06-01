# -*- coding: utf-8 -*-
# DeepSeek 对话模块

import os
import json
import time

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox

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
        self.deep_key_file = os.path.join(CUR_DIR, "deepseek_key.json")
        saved_key = self._load_deepseek_key()
        self.deep_client = DeepSeekClient(api_key=saved_key)
        self.deep_history = []
        self._deep_loading_history = False
        self._wx_auto_reply = False
        self._deep_hook_mute_until = 0
        self._deep_last_bot_reply = ""
        self.history_file = os.path.join(CUR_DIR, "chat_history.json")
        if saved_key and hasattr(self, "ledt_2_deepseek_key"):
            self.ledt_2_deepseek_key.setText(saved_key)

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
        self.btn_1_start.clicked.connect(self.on_deep_start)
        self.btn_1_stop.clicked.connect(self.on_deep_stop)
        if hasattr(self, "btn_2_shuaxin"):
            self.btn_2_shuaxin.clicked.connect(self.updateGroupList)

        self.load_deep_history()
        self._update_deep_status()

    def _load_deepseek_key(self):
        if os.path.exists(self.deep_key_file):
            try:
                with open(self.deep_key_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                key = (data.get("api_key") or "").strip()
                if key:
                    return key
            except Exception:
                pass
        return os.environ.get("DEEPSEEK_API_KEY", "").strip() or None

    def _save_deepseek_key(self, key):
        try:
            with open(self.deep_key_file, "w", encoding="utf-8") as f:
                json.dump({"api_key": key}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def on_change_deepseek_key(self):
        key = self.ledt_2_deepseek_key.text().strip()
        if not key:
            self.lb_1_0.setText("请输入 DeepSeek API Key")
            QMessageBox.warning(self, "提示", "请输入 DeepSeek API Key", QMessageBox.Ok)
            return
        self.deep_client.api_key = key
        os.environ["DEEPSEEK_API_KEY"] = key
        self._save_deepseek_key(key)
        self.lb_1_0.setText("DeepSeek Key 已更新")
        QMessageBox.information(self, "提示", "DeepSeek API Key 已更换并生效", QMessageBox.Ok)

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

    def _get_ignore_senders(self):
        names = set()
        if not hasattr(self, "tableWidget_2"):
            return names
        for row in range(self.tableWidget_2.rowCount()):
            item = self.tableWidget_2.item(row, 0)
            if item:
                text = item.text().strip()
                if text:
                    names.add(text)
        return names

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

    def on_deep_start(self):
        self._save_selected_groups()
        groups = self._get_monitor_group_wxids()
        if not groups:
            self.lb_1_0.setText("请先在设置页选择接单群或飞单群")
            QMessageBox.warning(
                self, "提示",
                "请先在「设置」页选择接单群或飞单群，并点击「刷新群列表」。",
                QMessageBox.Ok,
            )
            return
        self._wx_auto_reply = True
        self.hasLogin = True
        self._update_deep_status()
        self.lb_1_0.setText("微信 Hook 已开启，监听接单群/飞单群消息")
        if hasattr(self, "wxHdInit"):
            if not getattr(self, "canUseWx", False):
                self.wxHdInit()
            elif hasattr(self, "updateGroupList"):
                self.updateGroupList()

    def on_deep_stop(self):
        self._wx_auto_reply = False
        self._update_deep_status()

    def on_deep_send(self):
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
        # if not self._wx_auto_reply:
        #     return
        # if self._is_hook_muted():
        #     return

        msgtype = json_dict.get("msgtype")
        if msgtype not in (1, "1"):
            return

        content = json_dict.get("content", "")
        if not content or not str(content).strip():
            return

        reply_wxid = self._resolve_reply_wxid(json_dict)
        if not reply_wxid:
            return

        monitor_groups = self._get_monitor_group_wxids()
        if reply_wxid not in monitor_groups:
            return

        nickname, pure_content = self._parse_wx_content(str(content))
        if not pure_content:
            return
        if self._is_bot_echo(pure_content):
            return

        ignore = self._get_ignore_senders()
        if nickname and nickname in ignore:
            return
        if reply_wxid in ignore:
            return

        sender = self._sender_label(json_dict, nickname, reply_wxid)
        jd_wxid = self.getJieDanQun1() if hasattr(self, "getJieDanQun1") else ""
        fd_wxid = self.getFdQun1() if hasattr(self, "getFdQun1") else ""
        if reply_wxid == jd_wxid:
            group_label = "接单群"
        elif reply_wxid == fd_wxid:
            group_label = "飞单群"
        else:
            group_label = "群聊"
        display_sender = "[%s] %s" % (group_label, sender)
        self.append_deep_message(display_sender, pure_content)
        self.lb_1_0.setText("DeepSeek 正在回复 %s..." % group_label)
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
