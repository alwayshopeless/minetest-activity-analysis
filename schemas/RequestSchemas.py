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
    players = fields.List(required=True, cls_or_instance=fields.String,
                          metadata={
                              "description": "A list of players",
                              "example": ['Player1', "Player2"],
                          })
    actions = fields.List(required=True, cls_or_instance=fields.String,
                          metadata={
                              "description": "A list of actions: places node, digs, moves, takes",
                              "example": ['places node', "takes", "moves"],
                          })
    dateFrom = fields.String(required=False, default=None, missing=None, data_key="from",
                             metadata={
                                 "description": "Date in format dd-mm-yyyy hh:ii",
                                 "example": "31-12-2020"
                             })
    dateTo = fields.String(required=False, default=None, missing=None, data_key="to",
                           metadata={
                               "description": "Date in format dd-mm-yyyy hh:ii",
                               "example": "31-12-2020"
                           })

    @post_load
    def asdsad(self, data, **kwargs):
        data['dateFrom'] = int(dateStrToTimestamp(data['dateFrom'])) if data['dateFrom'] else None
        data['dateTo'] = int(dateStrToTimestamp(data['dateTo'])) if data['dateTo'] else None
        return data


class LogsSchema(PlayerActionSchema):
    pass


class ClustersSchema(PlayerActionSchema):
    mode = fields.String(missing='2d', validate=validate.OneOf(['2d', '3d']),
                         metadata={
                             "description": "Mode for calculating clusters, 2d can speed up calculation. Default: 3D",
                             "example": "2d"
                         }
                         )
    onlyCount = fields.Boolean(missing=False,
                               metadata={
                                   "description": "Show only count for group positions",
                                   "example": True
                               }
                               )


class ActivityByPosSchema(ClustersSchema):
    pos = fields.List(cls_or_instance=fields.Int, required=True,
                      metadata={
                          "description": "Center position",
                          "example": [0, 0, 0]
                      }

                      )
    radius = fields.Int(
        missing=100,
        metadata={
            "description": "Radius, default 100",
            "example": 54
        }

    )


class AuthActivitySchema(Schema):
    players = fields.List(
        required=True, cls_or_instance=fields.String,
        metadata={
            "description": "A list of players",
            "example": ['Player1', "Player2"],
        }
    )


class IpsHistorySchema(Schema):
    players = fields.List(
        required=True, cls_or_instance=fields.String,
        metadata={
            "description": "A list of players",
            "example": ['Player1', "Player2"],
        }
    )


class IpsHistoryByMaskSchema(Schema):
    ipMasks = fields.List(
        required=True,
        cls_or_instance=fields.String,
        data_key='ips',

        metadata={
            "description": "List of IPs or their parts",
            "example": [
                "37.123.",
                "127.0.",
                "192.168.",
                "87.123.23.123"
            ],
        })
