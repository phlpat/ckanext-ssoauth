# -*- coding: utf-8 -*-

import logging
from sqlalchemy import Table, select, insert, text 

import ckan.plugins as p
import ckan.model as model

from passlib.hash import pbkdf2_sha512
from datetime import datetime, date
from uuid import UUID
import json

log = logging.getLogger(__name__)

def table(name):
    return Table(name, model.meta.metadata, autoload=True)

class Helper():

    # def generate_password_hash(self, password):
    #     hash_str = pbkdf2_sha512.hash(rounds=25000, salt="5nyvde4dIwTAeM.Zk7JWag").hash(password)
    #     return hash_str

    def create_user(self, email, username, firstName, lastName):
        hashed_password = "test1"

        user_table = table('user')
        insert_stmt = insert(user_table).values(
            name=username,
            password=hashed_password,
            fullname= firstName + " " + lastName,
            email=email,
            sysadmin=False
        )

        try:
            connection = model.Session.connection()
            connection.execute(insert_stmt)
            model.Session.commit()
            return "user created"
        except Exception as e:
            log.error(e)
            model.Session.rollback()
            return "error creating user"
        
    def get_user(self, username):
        user_table = table('user')
        query = select([user_table]).where(
            (user_table.c.name == username)
        )
        connection = model.Session.connection()
        result = connection.execute(query).fetchone()
        if result:
            user_data = dict(result.items())
            return json.dumps(user_data, default=self.custom_json_encoder)
        else:
            return None

    #check user exists
    def identify(self, email, username, firstName, lastName):
        user_table = table('user')
        query = select([user_table]).where(
            (user_table.c.name == email) &
            (user_table.c.fullname.ilike(firstName + " " + lastName))
        )
        connection = model.Session.connection()
        result = connection.execute(query).fetchone()
        if result:
            return True
        else:
            return False
        
    @staticmethod
    def custom_json_encoder(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
