import smtplib

from i18n import translate


class MemoryTransport:
    def __init__(self):
        self.messages = []

    def send(self, subject, body):
        self.messages.append({"subject": subject, "body": body})
        return True


class SmtpTransport:
    def __init__(self, host, port=25, from_addr="vibrasense@localhost", use_tls=False):
        self.host = host
        self.port = int(port)
        self.from_addr = from_addr
        self.use_tls = use_tls

    def send(self, subject, body):
        message = "Subject: %s\n\n%s" % (subject, body)
        with smtplib.SMTP(self.host, self.port, timeout=10) as client:
            if self.use_tls:
                client.starttls()
            client.sendmail(self.from_addr, [self.from_addr], message)
        return True


class AlertRouter:
    def __init__(self, transports=None):
        self.transports = list(transports or [])

    def publish(self, node_id, state, reason, language="en"):
        subject = translate(language, "alert_subject", node=node_id, state=state)
        body = translate(language, "alert_body", node=node_id, state=state, reason=reason)
        results = [transport.send(subject, body) for transport in self.transports]
        return bool(results) and all(results)
