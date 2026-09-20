from datenbank.SQL_db import open_db_conn
from pathlib import Path
import hashlib

class ReleaseNotFoundError(Exception):
    pass

class ReleaseAlreadyExistsError(Exception):
    pass

class ReleaseNotActiveError(Exception):
    pass

class ReleaseNotAddedError(Exception):
    pass

class NoActiveVersionError(Exception):
    pass

class MultActiveVersionError(Exception):
    pass



def get_file_metadata(location):
    file_path = Path(location)
    size = file_path.stat().st_size
    sha256 = hashlib.sha256()
    with open(location,"rb",) as exe:
        while True:
            chunk = exe.read(8192)
            if not chunk:
                break
            sha256.update(chunk)


    checksum =  sha256.hexdigest()

    return size, checksum



def add_release(version, location) -> bool:
    with open_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM releases WHERE version = %s",
                        (version, ))
            version_exist = cur.fetchone()
            if version_exist:
                raise ReleaseAlreadyExistsError()
            size, checksum = get_file_metadata(location)


            cur.execute("INSERT INTO releases(version, size, location, checksum) VALUES(%s,%s,%s,%s) RETURNING version",
                        (version, size, location, checksum))
            version_added = cur.fetchone()
            if not version_added:
                raise ReleaseNotAddedError()
            return True



def activate_version(version) -> bool:
    with open_db_conn() as conn:
        with conn.cursor() as cur:


            cur.execute("SELECT version FROM releases WHERE version = %s",
                        (version, ))
            does_version_exist = cur.fetchone()
            if not does_version_exist:
                raise ReleaseNotFoundError()


            cur.execute("UPDATE releases SET active = false")

                
            cur.execute("UPDATE releases SET active = true WHERE version = %s RETURNING active, version",
                        (version, ))
            is_version_active = cur.fetchone()
            if not is_version_active:
                raise ReleaseNotActiveError()

            if not is_version_active[0]:
                raise ReleaseNotActiveError()
            return True


def get_active_release():
        with open_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version, release_date, size, location, checksum FROM releases WHERE active = true")
                active_versions = cur.fetchall()
                if not active_versions:
                    raise NoActiveVersionError()

                if len(active_versions) > 1:
                    raise MultActiveVersionError()
                active_version = {
                            "version": active_versions[0][0],
                            "release_date": active_versions[0][1],
                            "size": active_versions[0][2],
                            "location": active_versions[0][3],
                            "checksum": active_versions[0][4]
                        }
                return active_version

def show_versions():
        releases_list = []
        with open_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM releases")
                all_releases = cur.fetchall()
                for release in all_releases:
                    releases_list.append(
                        {
                        "version": release[0],
                        "release_date": release[1],
                        "size": release[2],
                        "location": release[3],
                        "checksum": release[4],
                        "active": release[5]
                        }
                    )
                return releases_list
