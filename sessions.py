from cherrypy.lib.sessions import RamSession as cpRamSession

class RamSession(cpRamSession):
    def clean_up(self):
        """Clean up expired sessions."""

        now = self.now()
        try:
            for _id, (data, expiration_time) in list(self.cache.items()):
                if expiration_time <= now:
                    try:
                        del self.cache[_id]
                    except KeyError:
                        pass
                    try:
                        if self.locks[_id].acquire(blocking=False):
                            lock = self.locks.pop(_id)
                            lock.release()
                    except KeyError:
                        pass

        except RuntimeError:
            """Under heavy load, list(self.cache.items()) will occasionally raise this error
            for large session caches with message "dictionary changed size during iteration"
            Better to pause the cleanup than to let the cleanup thread die.
            """

            return 

        # added to remove obsolete lock objects
        for _id in list(self.locks):
            locked = (
                _id not in self.cache
                and self.locks[_id].acquire(blocking=False)
            )
            if locked:
                lock = self.locks.pop(_id)
                lock.release()
