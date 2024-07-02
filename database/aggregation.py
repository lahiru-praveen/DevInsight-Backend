import pymongo

get_next_operator_id_pipeline = lambda user: [
    {
        '$match': {
            'user': user
        }
    },
    {
        '$sort': {
            'p_id': pymongo.DESCENDING
        }
    },
    {
        '$limit': 1
    },
    {
        '$project': {
            '_id': 0,
            'next_p_id': {
                '$add': [{'$ifNull': ['$p_id', 0]}, 1]
            }
        }
    }
]
