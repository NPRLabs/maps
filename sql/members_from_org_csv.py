import argparse
import csv
import sqlite3
import sys
import random
import time
import sys
import math

#c.execute(UPDATE {} SET member=? WHERE callsign LIKE ?

find_parent_sql = "SELECT * FROM orgs WHERE parentcallsign LIKE ?"
org_insert_sql = "INSERT INTO orgs VALUES(?,?,?)"

def update_org_id(table):
    return "UPDATE {} SET org=?, member=? WHERE id=?".format(table)

def update_org_callsign(table):
    return "UPDATE {} SET org=? WHERE callsign=? or callsign=?".format(table)


def update_org(db, c, parent_callsign, ptable, ctable, id_to_update, status):
    c.execute(find_parent_sql, (parent_callsign+'%',))
    orgs = c.fetchall()
    if id_to_update == 1695:
        print 'YES'
    if len(orgs) == 1:
        c.execute(update_org_id(ctable), (orgs[0][0], status, id_to_update,))
        c.execute(update_org_callsign(ptable), 
                    (orgs[0][0], parent_callsign.split('-')[0], parent_callsign))
    elif len(orgs) == 0:
        #make new org entry
        c.execute(org_insert_sql, (None, parent_callsign, None))

        #get id
        c.execute(find_parent_sql, (parent_callsign+'%',))
        org = c.fetchone()

        c.execute(update_org_id(ctable), (org[0], status, id_to_update,))
        #also have to set the parent's org
        c.execute(update_org_callsign(ptable),
                    (org[0], parent_callsign.split('-')[0], parent_callsign))
        
    else:
        #shouldn't happen
        print "ORG TABLE MESSED UP"
        pass

    #db.commit()
    


def set_orgs():
    db = sqlite3.connect('fcc.db')
    c = db.cursor()
    with open('data/orgs.csv') as csvfile:
        list_reader = csv.DictReader(csvfile)
        for line in list_reader:
            splitup = line['associate calletter'].split('-')
            ctable = splitup[1].lower().strip()
            if splitup[0] == 'WBAA':
                print splitup
            ptable = line['parent calletter'].split('-')[1].lower().strip()
            c.execute("SELECT * FROM {} WHERE callsign=?"
                .format(ctable), (splitup[0],))
            output = c.fetchall()
            if len(output) == 1:
                ''' EXACTLY ONE MATCH GOOD'''
                update_org(db, c, line['parent calletter'], ptable, ctable, output[0][0]
                        , line['stationstatus'])
            elif len(output) > 1:
                c.execute('SELECT * FROM {} WHERE callsign=? and service=? and status=?'''
                    .format(ctable), (splitup[0], ctable.upper(), 'LIC'))

                new_output = c.fetchall()
                #gonna need to update both
                if len(new_output) > 1:

                    '''
                    s = "SELECT * FROM {} WHERE callsign=? and service=? and status=?"
                        .format(splitup[1].lower().strip())
                    c.execute(s, (splitup[0],splitup[1].strip(),'LIC'))
                    o = c.fetchall()
                    if len(o) == 0:
                        c.execute('SELECT * FROM {} WHERE callsign=? and service=
                            .format(splitup[1].lower().strip()), 
                                (line['associate calletter'],splitup[1].strip()))
                        if len(c.fetchall()) == 0:
                            print 'bad3333'
                    elif len(o) > 1:
                        print len(o)
                        
                        print splitup
                        print 'uh oh'
                        '''
                    '''UPATING FIRST OF THEM'''
                    for n in xrange(0, len(new_output)):
                        update_org(db, c, line['parent calletter'], 
                                ptable, ctable, new_output[n][0], line['stationstatus'])


                elif len(new_output) == 0:
                    c.execute('SELECT * FROM {} WHERE callsign=? and service=?'''
                        .format(ctable), (splitup[0], ctable.upper()))
                    print c.fetchall()
                    print splitup
                    print output
                    print 'bad1'
                else:
                    ''' EXACTLY ONE MATCH GOOD'''
                    update_org(db, c, line['parent calletter'], 
                            ptable, ctable, output[0][0], line['stationstatus'])

            else:
                c.execute("SELECT * FROM {} WHERE callsign LIKE ?"
                    .format(ctable), (splitup[0]+'%',))
                output = c.fetchall()
                if len(output) == 1:
                    ''' EXACTLY ONE MATCH GOOD'''
                    update_org(db, c, line['parent calletter'], 
                            ptable, ctable, output[0][0], line['stationstatus'])
                elif len(output) > 1:
                    c.execute('SELECT * FROM {} WHERE callsign=? and service=? and status=?'''
                        .format(ctable), (splitup[0], ctable.upper(), 'LIC'))
                    new_output = c.fetchall()
                    #gonna need to update both
                    if len(new_output) > 1:
                        '''UPATING FIRST OF THEM'''
                        update_org(db, c, line['parent calletter'], 
                                ptable, ctable, new_output[0][0], line['stationstatus'])


                else:
                    print "Not in database:{}".format(splitup[0])
                    print "What do we do here?"
                    print

    # Explicitly check "member-less" parents
    
    print "FM:"
    c.execute("SELECT * FROM fm WHERE member ISNULL and org NOT NULL and status='LIC'")
    print c.fetchall()
    print "AM:"
    c.execute("SELECT * FROM am WHERE member ISNULL and org NOT NULL and status='LIC'")
    print c.fetchall()

    db.commit()
    db.close()


if __name__ == '__main__':
    set_orgs()

