# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 14:46:42 2015

@author: dhuling, geomando
"""
from household import Household
from resources import Resources, Containers
import config, util
import csv, random
import sqlite3
import pandas as pd

class DataBase (object):

    def __init__(self, path):
        self.db_connect(path)


    def db_connect(self, path):
        db = path
        self.con = sqlite3.connect(db, isolation_level=None)
        self.cur = self.con.cursor()

    def db_refresh_tables(self):
        """this method deletes old tables (including ALL records) and recreates
        them in the same schema. """
        self.con.execute("begin")
        delete_old_tables = """
                            DROP table IF EXISTS household;
                            DROP table IF EXISTS params;
                            DROP table IF EXISTS coords
                            """
        self.cur.executescript(delete_old_tables)
        create = """CREATE table household (
                            name INTEGER,
                            income INTEGER,
                            insp_time INTEGER,
                            insure_time INTEGER,
                            rebuild_time INTEGER,
                            damage INTEGER,
                            total_funds INTEGER,
                            sim_run INTEGER);
                    CREATE table params (
                            num_insp INTEGER,
                            num_loan_off INTEGER,
                            num_contractors INTEGER,
                            fema INTEGER,
                            sim_run INTEGER PRIMARY KEY);
                    CREATE table coords (
                            name INTEGER,
                            long REAL,
                            lat REAL);
                            """
        self.cur.executescript(create)
        self.con.commit()

    def db_save(self, households, params, simulation_run):
        self.con.execute("begin")
        for i in households:
            statement = [households[i].name,
                         households[i].income,
                         households[i].inspection_time,
                         households[i].ins_claim_time,
                         households[i].rebuild_stop,
                         households[i].damage,
                         households[i].total_funds,
                         simulation_run
                         ]
            self.con.execute("""INSERT into household
                           (name,
                            income,
                            insp_time,
                            insure_time,
                            rebuild_time,
                            damage,
                            total_funds,
                            sim_run
                            )
                   values (?,
                           ?,
                           ?,
                           ?,
                           ?,
                           ?,
                           ?,
                           ?
                           )""",
                           statement
                           )

        ############ ---- END OF ABOVE FOR LOOP --- ###########
        #this commits the above transactions. there are ~10000 per commit
        self.con.commit()

        #begin new transaction
        self.con.execute("begin")
        self.con.execute("""INSERT into params
                            (num_insp,
                             num_loan_off,
                             num_contractors,
                             fema,
                             sim_run
                             )
                       values
                            (?,
                             ?,
                             ?,
                             ?,
                             ?
                             )""",
                             params
                             )
        self.con.commit()

    def db_close(self):
        self.con.close()

    def db_coords(self, coord_path):
        coords = get_coords(coord_path)
        self.con.execute("BEGIN")
        for i in xrange(len(coords)):
            coords_statement=[coords[i][0],
                              coords[i][1],
                              coords[i][2]]
            self .con.execute("""INSERT into coords
                                    (name,
                                     long,
                                     lat)
                                 VALUES
                                    (?,
                                     ?,
                                     ?)""",
                                     coords_statement)
        self.con.commit()
