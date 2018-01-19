from IPy import IP


class Common(object):

    @staticmethod
    def is_ip(ip):
      try:
          IP(ip)
          return True
      except ValueError, e:
          return False