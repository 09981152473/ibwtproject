            if hasattr(_ssl, 'sslwrap'):
                if ciphers is None:
                    self._sslobj = _ssl.sslwrap(self._sock, server_side,
                                                keyfile, certfile,
                                                cert_reqs, ssl_version, ca_certs)
                else:
                    self._sslobj = _ssl.sslwrap(self._sock, server_side,
                                                keyfile, certfile,
                                                cert_reqs, ssl_version, ca_certs,
                                                ciphers)
            else:
                self.context = __ssl__.SSLContext(ssl_version)
                self.context.verify_mode = cert_reqs
                if ca_certs:
                    self.context.load_verify_locations(ca_certs)
                if certfile:
                    self.context.load_cert_chain(certfile, keyfile)
                if ciphers:
                    self.context.set_ciphers(ciphers)
                self._sslobj = self.context._wrap_socket(self._sock, server_side=server_side, ssl_sock=self)
