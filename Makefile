# run the server
run-server:
	python3 TCPServer.py

# run the client
run-client:
	python3 TCPClient.py

# clean up database cache
filenames := users.json
files := $(strip $(foreach f,$(filenames),$(wildcard $(f))))
clean:
ifneq ($(files),)
	rm -f $(files)
endif
	clear