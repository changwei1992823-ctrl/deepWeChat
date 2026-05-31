# -*- coding: utf-8 -*-
# DeepSeek 对话模块

import os
import json

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QMainWindow, QApplication

from common_init import *
from deepseek_client import DeepSeekClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class deepHandle(object):
    """DeepSeek 聊天与微信消息自动回复"""

    def deepInit(self):
        self.deep_client = DeepSeekClient()
        self.deep_history = []
        self._deep_loading_history = False
        self._wx_auto_reply = False
        self.history_file = os.path.join(CUR_DIR, "chat_history.json")

        self.chat_view.setOpenExternalLinks(True)
        self.chat_view.setStyleSheet(
            "QTextBrowser { background-color:#F7F7F7; border:1px solid #CCCCCC; padding:10px; }"
        )
        self.query.installEventFilter(self)

        self.clear_btn.clicked.connect(self.clear_deep_history)
        self.btn_1_shoudong.clicked.connect(self.on_deep_send)
        self.btn_1_start.clicked.connect(self.on_deep_start)
        self.btn_1_stop.clicked.connect(self.on_deep_stop)

        self.load_deep_history()
        self._update_deep_status()

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
        self.deep_history = []
        self.chat_view.clear()
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except Exception:
            pass

    def on_deep_start(self):
        self._wx_auto_reply = True
        self.hasLogin = True
        self._update_deep_status()
        if hasattr(self, "wxHdInit") and not getattr(self, "canUseWx", False):
            self.wxHdInit()

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
        if not self._wx_auto_reply:
            return

        msgtype = json_dict.get("msgtype")
        if msgtype not in (1, "1"):
            return

        content = json_dict.get("content", "")
        if not content or not str(content).strip():
            return

        wxid = json_dict.get("wxid", "")
        if not wxid:
            return

        nickname, pure_content = self._parse_wx_content(str(content))
        if not pure_content:
            return

        sender = nickname or self._wx_display_name(wxid)
        self.append_deep_message(sender, pure_content)

        response_text = self._call_deepseek(pure_content)
        self.append_deep_message("DeepSeek", response_text)

        if getattr(self, "canUseWx", False) and hasattr(self, "sendTextMsg0"):
            self.sendTextMsg0(response_text, wxid)

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
        if hasattr(self, "query") and watched is self.query and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.on_deep_send()
                return True
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
                self.query.insertPlainText("\n")
                return True
        return QMainWindow.eventFilter(self, watched, event)
