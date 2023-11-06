from datetime import datetime

from marshmallow import Schema, fields, post_load, validate


def dateStrToTimestamp(date):
    date_format = "%d-%m-%Y %H:%M"
    try:
        date_obj = datetime.strptime(date, date_format)
        if date_obj:
            timestamp = date_obj.timestamp()
            return timestamp
        else:
            return None
    except ValueError:
        return None


class PlayerActionSchema(Schema):
    players = fields.List(required=True, cls_or_instance=fields.String)
    actions = fields.List(required=True, cls_or_instance=fields.String)
    dateFrom = fields.String(required=False, default=None, missing=None, data_key="from")
    dateTo = fields.String(required=False, default=None, missing=None, data_key="to")

    @post_load
    def asdsad(self, data, **kwargs):
        data['dateFrom'] = int(dateStrToTimestamp(data['dateFrom'])) if data['dateFrom'] else None
        data['dateTo'] = int(dateStrToTimestamp(data['dateTo'])) if data['dateTo'] else None
        return data


class LogsSchema(PlayerActionSchema):
    pass


class ClustersSchema(PlayerActionSchema):
    mode = fields.String(missing='2d', validate=validate.OneOf(['2d', '3d']))
    onlyCount = fields.Boolean(missing=False)


class ActivityByPosSchema(ClustersSchema):
    pos = fields.List(cls_or_instance=fields.Int, required=True)
    radius = fields.Int(missing=100)

class AuthActivitySchema(Schema):
    players = fields.List(required=True, cls_or_instance=fields.String)

class IpsHistorySchema(Schema):
    players = fields.List(required=True, cls_or_instance=fields.String)

class IpsHistoryByMaskSchema(Schema):
    ipMasks = fields.List(required=True, cls_or_instance=fields.String, data_key='ips')
