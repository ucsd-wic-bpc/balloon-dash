#
# Autogenerated by Thrift Compiler (1.0.0-dev)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
import sys

from thrift.transport import TTransport


class CompetitionSettings(object):
    """
    Attributes:
     - alert_thresholds
     - stub
     - username
     - password
     - categories
     - tags
    """

    thrift_spec = (
        None,  # 0
        (1, TType.LIST, 'alert_thresholds', (TType.I32, None, False), None, ),  # 1
        (2, TType.STRING, 'stub', 'UTF8', None, ),  # 2
        (3, TType.STRING, 'username', 'UTF8', None, ),  # 3
        (4, TType.STRING, 'password', 'UTF8', None, ),  # 4
        (5, TType.MAP, 'categories', (TType.STRING, 'UTF8', TType.STRING, 'UTF8', False), None, ),  # 5
        (6, TType.MAP, 'tags', (TType.STRING, 'UTF8', TType.LIST, (TType.STRING, 'UTF8', False), False), None, ),  # 6
    )

    def __init__(self, alert_thresholds=None, stub=None, username=None, password=None, categories=None, tags=None,):
        self.alert_thresholds = alert_thresholds
        self.stub = stub
        self.username = username
        self.password = password
        self.categories = categories
        self.tags = tags

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.LIST:
                    self.alert_thresholds = []
                    (_etype3, _size0) = iprot.readListBegin()
                    for _i4 in range(_size0):
                        _elem5 = iprot.readI32()
                        self.alert_thresholds.append(_elem5)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRING:
                    self.stub = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.STRING:
                    self.username = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.STRING:
                    self.password = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.MAP:
                    self.categories = {}
                    (_ktype7, _vtype8, _size6) = iprot.readMapBegin()
                    for _i10 in range(_size6):
                        _key11 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        _val12 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        self.categories[_key11] = _val12
                    iprot.readMapEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.MAP:
                    self.tags = {}
                    (_ktype14, _vtype15, _size13) = iprot.readMapBegin()
                    for _i17 in range(_size13):
                        _key18 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        _val19 = []
                        (_etype23, _size20) = iprot.readListBegin()
                        for _i24 in range(_size20):
                            _elem25 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                            _val19.append(_elem25)
                        iprot.readListEnd()
                        self.tags[_key18] = _val19
                    iprot.readMapEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('CompetitionSettings')
        if self.alert_thresholds is not None:
            oprot.writeFieldBegin('alert_thresholds', TType.LIST, 1)
            oprot.writeListBegin(TType.I32, len(self.alert_thresholds))
            for iter26 in self.alert_thresholds:
                oprot.writeI32(iter26)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.stub is not None:
            oprot.writeFieldBegin('stub', TType.STRING, 2)
            oprot.writeString(self.stub.encode('utf-8') if sys.version_info[0] == 2 else self.stub)
            oprot.writeFieldEnd()
        if self.username is not None:
            oprot.writeFieldBegin('username', TType.STRING, 3)
            oprot.writeString(self.username.encode('utf-8') if sys.version_info[0] == 2 else self.username)
            oprot.writeFieldEnd()
        if self.password is not None:
            oprot.writeFieldBegin('password', TType.STRING, 4)
            oprot.writeString(self.password.encode('utf-8') if sys.version_info[0] == 2 else self.password)
            oprot.writeFieldEnd()
        if self.categories is not None:
            oprot.writeFieldBegin('categories', TType.MAP, 5)
            oprot.writeMapBegin(TType.STRING, TType.STRING, len(self.categories))
            for kiter27, viter28 in self.categories.items():
                oprot.writeString(kiter27.encode('utf-8') if sys.version_info[0] == 2 else kiter27)
                oprot.writeString(viter28.encode('utf-8') if sys.version_info[0] == 2 else viter28)
            oprot.writeMapEnd()
            oprot.writeFieldEnd()
        if self.tags is not None:
            oprot.writeFieldBegin('tags', TType.MAP, 6)
            oprot.writeMapBegin(TType.STRING, TType.LIST, len(self.tags))
            for kiter29, viter30 in self.tags.items():
                oprot.writeString(kiter29.encode('utf-8') if sys.version_info[0] == 2 else kiter29)
                oprot.writeListBegin(TType.STRING, len(viter30))
                for iter31 in viter30:
                    oprot.writeString(iter31.encode('utf-8') if sys.version_info[0] == 2 else iter31)
                oprot.writeListEnd()
            oprot.writeMapEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class User(object):
    """
    Attributes:
     - username
     - completed_problems
     - acked_alerts
     - pending_alerts
     - category
     - tags
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRING, 'username', 'UTF8', None, ),  # 1
        (2, TType.I32, 'completed_problems', None, None, ),  # 2
        (3, TType.I32, 'acked_alerts', None, None, ),  # 3
        (4, TType.I32, 'pending_alerts', None, None, ),  # 4
        (5, TType.STRING, 'category', 'UTF8', None, ),  # 5
        (6, TType.LIST, 'tags', (TType.STRING, 'UTF8', False), None, ),  # 6
    )

    def __init__(self, username=None, completed_problems=None, acked_alerts=None, pending_alerts=None, category=None, tags=None,):
        self.username = username
        self.completed_problems = completed_problems
        self.acked_alerts = acked_alerts
        self.pending_alerts = pending_alerts
        self.category = category
        self.tags = tags

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.username = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I32:
                    self.completed_problems = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.acked_alerts = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.I32:
                    self.pending_alerts = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRING:
                    self.category = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.LIST:
                    self.tags = []
                    (_etype35, _size32) = iprot.readListBegin()
                    for _i36 in range(_size32):
                        _elem37 = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                        self.tags.append(_elem37)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('User')
        if self.username is not None:
            oprot.writeFieldBegin('username', TType.STRING, 1)
            oprot.writeString(self.username.encode('utf-8') if sys.version_info[0] == 2 else self.username)
            oprot.writeFieldEnd()
        if self.completed_problems is not None:
            oprot.writeFieldBegin('completed_problems', TType.I32, 2)
            oprot.writeI32(self.completed_problems)
            oprot.writeFieldEnd()
        if self.acked_alerts is not None:
            oprot.writeFieldBegin('acked_alerts', TType.I32, 3)
            oprot.writeI32(self.acked_alerts)
            oprot.writeFieldEnd()
        if self.pending_alerts is not None:
            oprot.writeFieldBegin('pending_alerts', TType.I32, 4)
            oprot.writeI32(self.pending_alerts)
            oprot.writeFieldEnd()
        if self.category is not None:
            oprot.writeFieldBegin('category', TType.STRING, 5)
            oprot.writeString(self.category.encode('utf-8') if sys.version_info[0] == 2 else self.category)
            oprot.writeFieldEnd()
        if self.tags is not None:
            oprot.writeFieldBegin('tags', TType.LIST, 6)
            oprot.writeListBegin(TType.STRING, len(self.tags))
            for iter38 in self.tags:
                oprot.writeString(iter38.encode('utf-8') if sys.version_info[0] == 2 else iter38)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class NotWatchingCompetitionException(TException):
    """
    Attributes:
     - stub
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRING, 'stub', 'UTF8', None, ),  # 1
    )

    def __init__(self, stub=None,):
        self.stub = stub

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.stub = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('NotWatchingCompetitionException')
        if self.stub is not None:
            oprot.writeFieldBegin('stub', TType.STRING, 1)
            oprot.writeString(self.stub.encode('utf-8') if sys.version_info[0] == 2 else self.stub)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __str__(self):
        return repr(self)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class LeaderboardServerNotReadyException(TException):
    """
    Attributes:
     - message
    """

    thrift_spec = (
        None,  # 0
        (1, TType.STRING, 'message', 'UTF8', None, ),  # 1
    )

    def __init__(self, message=None,):
        self.message = message

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, (self.__class__, self.thrift_spec))
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.message = iprot.readString().decode('utf-8') if sys.version_info[0] == 2 else iprot.readString()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, (self.__class__, self.thrift_spec)))
            return
        oprot.writeStructBegin('LeaderboardServerNotReadyException')
        if self.message is not None:
            oprot.writeFieldBegin('message', TType.STRING, 1)
            oprot.writeString(self.message.encode('utf-8') if sys.version_info[0] == 2 else self.message)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __str__(self):
        return repr(self)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)