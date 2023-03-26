from django.db import models
from django.utils import timezone
import datetime
import logging
import subprocess
import telnetlib
import os
import requests
from django.core.mail import send_mail


class Time(models.Model):
    set_hours = models.IntegerField()
    set_minutes = models.IntegerField()
    set_seconds = models.IntegerField()


class Host(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255)
    port = models.CharField(max_length=20)
    last_check = models.DateTimeField('last check', default=timezone.now)
    last_status_change = models.DateTimeField('last status change', default=timezone.now)
    status_info = models.CharField(max_length=200, blank=True, default='')
    network = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True)
    DEFAULT = 0
    SUCCESS = 1
    INFO = 2
    WARNING = 3
    DANGER = 4
    STATUS_CHOICES = (
        (DEFAULT, 'secondary'),
        (SUCCESS, 'positive'),
        (INFO, 'primary'),
        (WARNING, 'warning'),
        (DANGER, 'negative'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=DEFAULT)
    logger = logging.getLogger(__name__)

    def __str__(self):
        return self.name


    @property
    def is_pinging(self):
        return not subprocess.call(f'ping {self.address}', shell=True)

    def log(self, message, level='debug'):
        log_message = f'{self.address:14} {message}'
        if level == 'info':
            self.logger.info(log_message)
        elif level == 'warning':
            self.logger.warning(log_message)
        else:
            self.logger.debug(log_message)

    def send_mail(self):
        icon = '\u2705' if self.status < self.WARNING else '\u274C'
        subject = 'THÔNG BÁO \u2714' if self.status < self.WARNING else 'THÔNG BÁO LỖI \u2757'
        if self.status < self.WARNING:
            message = f'WEBSITE: {self.name}\nĐỊA CHỈ: {self.address}\nCỔNG: {self.port}\n{icon}ĐÃ HOẠT ĐỘNG TRỞ LẠI{icon}\nMáy chủ đã được sửa chữa!'
        else:
            message = f'WEBSITE: {self.name}\nĐỊA CHỈ: {self.address}\nCỔNG: {self.port}\n{icon}ĐÃ NGỪNG HOẠT ĐỘNG{icon}\nMáy chủ có thể bị quá tải, sập nguồn hoặc không thể truy cập được do sự cố mạng, mất điện hoặc website đang được bảo trì...\nVui lòng kiểm tra lại máy chủ!'
        send_mail(
            f'{subject}',
            f'{message}',
            'lyb1809605@student.ctu.edu.vn',
            ['laibary0507@gmail.com'],
            fail_silently=False,
        )

    def send_telegram_message(self):

            token = '5515480940:AAEaf7B6mYCjHOW385Z0bYZ9SZPHazqhby8'
            chat_id = '-643309682'
            icon = '\u2705' if self.status < self.WARNING else '\u274C'
            if self.status < self.WARNING:
                message = f'WEBSITE: {self.name}\nĐỊA CHỈ: {self.address}\nCỔNG: {self.port}\n{icon}ĐÃ HOẠT ĐỘNG TRỞ LẠI{icon}\nMáy chủ đã được sửa chữa!'
            else:
                message = f'WEBSITE: {self.name}\nĐỊA CHỈ: {self.address}\nCỔNG: {self.port}\n{icon}ĐÃ NGỪNG HOẠT ĐỘNG{icon}\nMáy chủ có thể bị quá tải, sập nguồn hoặc không thể truy cập được do sự cố mạng, mất điện hoặc website đang được bảo trì...\nVui lòng kiểm tra lại máy chủ!'
            url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
            requests.get(url)

    def telnet(self):
        '''Telnet connection and get registered ports status'''
        try:
            tn = telnetlib.Telnet(self.address, self.port)
            tn.write(b"ls\n")
            tn.read_all()
            tn.close()
            return True
        except:
            return False

    def http_status(self):
        try:
            url = "http://" + self.address
            r = requests.head(url)
            print(r.status_code)
            http_code_ok = [100, 101, 102, 200, 201, 202, 203, 204, 205, 206, 207, 300, 301, 302, 303, 304, 305, 307, 308]
            if r.status_code in http_code_ok:
                return True
            else:
                return False
        except:
            return False

    def ping_and_update_status(self):
        '''Ping host, then telnet if there are registered ports'''
        if self.is_pinging:
            print('Ping SUCCESS')
            self.status = self.SUCCESS
            self.status_info = 'Up'
        else:
            print('Ping ERROR')
            self.status = self.DANGER
            self.status_info = 'Down'
        self.log(self.status_info)

    def telnet_and_update_status(self):
        '''Telnet host'''
        if self.telnet() and self.http_status():
            print('Telnet SUCCESS, Status OK')
            self.status = self.SUCCESS
            self.status_info = 'Up'
        else:
            print('Telnet ERROR, Status ERROR')
            self.status = self.DANGER
            self.status_info = 'Down'
        self.log(self.status_info)

    def update_log(self):
        '''Add new host log and remove old logs based on MAX_LOG_LINES'''
        try:
            max_log_lines = os.getenv('MAX_LOG_LINES', 20)
            HostLog.objects.create(host=self, status=self.status,
                                   status_info=self.status_info, status_change=self.last_status_change)
            HostLog.objects.filter(pk__in=HostLog.objects.filter(host=self).order_by('-status_change')
                                   .values_list('pk')[max_log_lines:]).delete()
            self.send_telegram_message()
            self.send_mail()
        except Exception as ex:
            self.log(ex, 'warning')

    def check_and_update(self):
        '''The 'main' function of monitord, check/update host and logs'''
        now = timezone.now()
        self.last_check = now
        # Only update changed fields in DB
        update_fields = ['last_check']
        # Store old data before change it
        old_status_info = self.status_info
        old_status = self.status
        self.ping_and_update_status()
        self.telnet_and_update_status()
        if old_status_info != self.status_info:
            self.log(f'Status info changed from "{old_status_info}" to "{self.status_info}"')
            self.last_status_change = now
            update_fields.extend(['last_status_change', 'status', 'status_info'])
            self.update_log()
            # check if change the status from danger to warning status
        elif self.status == self.DANGER:
            days_to_warning = os.getenv('DAYS_FROM_DANGER_TO_WARNING', 5)
            delta_limit_to_warning_status = now - datetime.timedelta(days=days_to_warning)
            if self.last_status_change <= delta_limit_to_warning_status:
                self.status = self.WARNING
                update_fields.extend(['status'])
        # Save only if the host was not deleted while in buffer
        try:
            self.save(update_fields=update_fields)
        except Exception as ex:
            self.log(ex, 'warning')


class HostLog(models.Model):
    '''Host Logs showed in host detail view'''
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=Host.STATUS_CHOICES, default=Host.DEFAULT)
    status_change = models.DateTimeField()
    status_info = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.host.name

