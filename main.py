# دُنگ‌یار با رابط Kivy برای ساخت نسخه APK اندروید با Buildozer

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.core.window import Window
import matplotlib.pyplot as plt
import locale
import re
import os

locale.setlocale(locale.LC_ALL, '')
Window.clearcolor = (0.96, 0.96, 0.96, 1)

class DongyarWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)
        self.entries = []
        self.amounts = []
        self.names = []
        self.show_chart = False

        self.add_widget(Label(text='دُنگ‌یار', font_size=24, bold=True))
        self.add_widget(Label(text='تعداد افراد را وارد کنید:', font_size=18))

        self.count_input = TextInput(multiline=False, font_size=16, input_filter='int')
        self.add_widget(self.count_input)

        self.start_btn = Button(text='ادامه', size_hint=(1, 0.2), on_press=self.create_form)
        self.add_widget(self.start_btn)

    def create_form(self, instance):
        try:
            count = int(self.count_input.text)
            if count <= 0:
                raise ValueError
        except:
            self.show_popup('خطا', 'تعداد معتبر وارد کنید.')
            return

        self.clear_widgets()
        self.add_widget(Label(text='اطلاعات افراد', font_size=20))

        self.scroll = ScrollView(size_hint=(1, 0.7))
        self.form_layout = GridLayout(cols=2, spacing=5, size_hint_y=None)
        self.form_layout.bind(minimum_height=self.form_layout.setter('height'))

        self.entries = []
        for _ in range(count):
            name_input = TextInput(hint_text='نام', font_size=16, multiline=False)
            amount_input = TextInput(hint_text='مبلغ پرداختی', font_size=16, multiline=False)
            self.entries.append((name_input, amount_input))
            self.form_layout.add_widget(name_input)
            self.form_layout.add_widget(amount_input)

        self.scroll.add_widget(self.form_layout)
        self.add_widget(self.scroll)

        chart_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.chart_checkbox = CheckBox()
        chart_layout.add_widget(Label(text='نمایش نمودار دایره‌ای'))
        chart_layout.add_widget(self.chart_checkbox)
        self.add_widget(chart_layout)

        self.calc_btn = Button(text='محاسبه دُنگ', size_hint=(1, 0.2), on_press=self.calculate)
        self.add_widget(self.calc_btn)

    def clean_amount(self, txt):
        clean = re.sub(r"[,.]", "", txt.replace(" ", ""))
        numbers = list(map(int, clean.split('+')))
        return sum(numbers)

    def format_amount(self, amount):
        return locale.format_string("%d", int(amount), grouping=True)

    def calculate(self, instance):
        try:
            names, amounts = [], []
            for name_input, amount_input in self.entries:
                name = name_input.text.strip()
                amount = self.clean_amount(amount_input.text.strip())
                if not name:
                    raise ValueError
                names.append(name)
                amounts.append(amount)
        except:
            self.show_popup('خطا', 'نام و مبلغ معتبر وارد کنید.')
            return

        total = sum(amounts)
        per_person = total / len(names)
        balances = [amt - per_person for amt in amounts]

        creditors = [(n, b) for n, b in zip(names, balances) if b > 0]
        debtors = [(n, -b) for n, b in zip(names, balances) if b < 0]

        transactions = []
        i = j = 0
        while i < len(debtors) and j < len(creditors):
            debtor_name, debtor_amt = debtors[i]
            creditor_name, creditor_amt = creditors[j]

            pay = min(debtor_amt, creditor_amt)
            transactions.append(f"{debtor_name} باید {self.format_amount(pay)} تومان به {creditor_name} بدهد")

            debtors[i] = (debtor_name, debtor_amt - pay)
            creditors[j] = (creditor_name, creditor_amt - pay)

            if debtors[i][1] == 0: i += 1
            if creditors[j][1] == 0: j += 1

        self.show_results(transactions, names, amounts)

    def show_results(self, transactions, names, amounts):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        if not transactions:
            layout.add_widget(Label(text='همه پرداخت‌ها برابرند.'))
        else:
            for t in transactions:
                layout.add_widget(Label(text=t, font_size=14))

        if self.chart_checkbox.active:
            self.save_chart(names, amounts, 'chart.png')
            layout.add_widget(Image(source='chart.png', size_hint=(1, 0.6)))

        popup = Popup(title='نتیجه محاسبه', content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def save_chart(self, names, amounts, path):
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=names, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.savefig(path, bbox_inches='tight', dpi=100)
        plt.close(fig)

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.7, 0.4))
        popup.open()

class DongyarApp(App):
    def build(self):
        return DongyarWidget()

if __name__ == '__main__':
    DongyarApp().run()
