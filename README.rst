=============
qemu-affinity
=============

``qemu-affinity`` is a tool to easily pin certain `QEMU <https://www.qemu.org>`_ threads to select CPU cores.

---------------
Getting Started
---------------

Installing
==========

This will install the ``qemu-affinity`` command to ``/usr/local/bin``.

From *pip*
----------

::

	pip install qemu-affinity
	
From source
-----------

Clone the repo and run::

	python setup.py install


Requirements
============

``qemu-affinity`` requires Python 3.

.. note::

	``qemu-system`` instances must be started with the ``-name <vm name>,debug-threads=on`` argument for ``qemu-affinity`` to correctly identify and set the affinity of specific *QEMU* threads.

Usage
=====

::

	qemu-affinity qemu-system-pid
				  [-h] [--dry-run] [-v] [-p [AFFINITY]]
				  [-q AFFINITY [AFFINITY ...]]
				  [-k THREAD_AFFINITY [THREAD_AFFINITY ...]]
				  [-i THREAD_AFFINITY [THREAD_AFFINITY ...]]
				  [-w THREAD_AFFINITY [THREAD_AFFINITY ...]]
				  [-t THREAD_AFFINITY [THREAD_AFFINITY ...]]
				  

Positional arguments
--------------------

``qemu-system-pid``
	PID of the qemu-system process

Optional arguments
------------------

``-h, --help``
	show this help message and exit
``--dry-run``
	don't modify thread affinity values (useful with ``-v``)
``-v, --verbose``
	be verbose
``-p AFFINITY``, ``--process-affinity AFFINITY``
	set *qemu-system* process affinity (and default for new threads)
``-q AFFINITY [AFFINITY ...]``, ``--qemu-affinity AFFINITY [AFFINITY ...]``
	set *qemu-system* thread affinity (partial name selectors not allowed)
``-k THREAD_AFFINITY [THREAD_AFFINITY ...]``, ``--kvm-affinity THREAD_AFFINITY [THREAD_AFFINITY ...]``
	set KVM (*CPU <n>/KVM*) thread affinity
``-i THREAD_AFFINITY [THREAD_AFFINITY ...]``, ``--io-affinity THREAD_AFFINITY [THREAD_AFFINITY ...]``
	set IO object (*IO <name>*) thread affinity
``-w THREAD_AFFINITY [THREAD_AFFINITY ...]``, ``--worker-affinity THREAD_AFFINITY [THREAD_AFFINITY ...]``
	set qemu worker (*worker*) thread affinity (partial name selectors not allowed, only positional)
``-t THREAD_AFFINITY [THREAD_AFFINITY ...]``, ``--thread-affinity THREAD_AFFINITY [THREAD_AFFINITY ...]``
	set arbitary (*<name>*) thread affinity

----

``AFFINITY`` is an *affinity-spec*

and

``THREAD_AFFINITY`` can be one of:

	* *affinity-spec*
	* *selector*\ ``:``\ *affinity-spec*
	


Where *affinity-spec* is a CPU number, a range (inclusive) of CPU numbers separated by a
dash (``-``), or a comma-delimited (``,``) list of CPU numbers or ranges.

	For example:
		
		``0``
			specifies CPU 0
		``0,1,2,3``
			specifies CPU 0, 1, 2 and 3
		``0-3``
			same as above
		``0,2-4,6``
			specifies CPU 0, 2, 3, 4 and 6


and, where *selector* is one of:

	* ``*``, meaning all threads
	* *partial-name* for ``-k`` (*CPU <partial-name>/KVM*) and ``-i`` (*IO <partial-name>*)
	* *name* for ``-t``
	

The first variant, *affinity-spec*, selects threads based on argument position.

	e.g., ``-k 0,4 1,5 2,6 3,7`` pins the first KVM thread to CPUs 0 and 4, the second KVM thread to CPUs 1 and 5, and so on.

The second variant, *selector*\ ``:``\ *affinity-spec*, selects threads by *selector*, which is a partial name or wildcard.
KVM threads have numeric names (*0*, *1*, *2*, etc.).
IO threads have user-supplied names (``-object iothread,id=``\ *name*).

	e.g., ``-k 2:2,6 -i myiothread:7 *:0`` pins KVM thread *2* (aka *CPU 2/KVM*) to CPUs 2 and 6, IO thread *myiothread* (aka *IO myiothread*) to CPU 7, and all remaining IO threads to
	CPU 0.

The two variants can be combined.
	
	e.g., ``-k 0,4 *:2,6`` pins the first KVM thread to CPUs 0 and 4,
		and all remaining KVM threads to CPUs 2 and 6.

-----------------
Known Limitations
-----------------

* the built-in help (``qemu-affinity -h``) lists the *qemu-system-pid* argument last in the list which may conflict with multi-argument parameters 
  such as ``-q``, ``-k``, ``-i``, ``-w``, and ``-t``.

	Either specify *qemu-system-pid* at the beginning of the argument list or use ``--`` to separate the multi-argument parameters from the positional parameters.

* ``-t/--thread-affinity`` only applies to the first of multiple threads that share an identical name (such as the QEMU ``worker`` threads).

	``-t`` is unable to specify different affinities for threads with duplicate names, nor is it able to apply the same affinity value to multiple threads with the same name
	(``*`` applies to *all* threads, not just a sub-set).
  
	e.g. ``-t abc:1 abc:2`` results in an error, and there is no way to set all threads with the name "abc" to the same affinity value.
  
	Additionally, there is no way to select the n\ :sup:`th` thread with the same name.
  
	e.g. ``-t abc:1`` will always select the 1\ :sup:`st` thread with the name "abc".

------------
Sample Usage
------------

The following *systemd.service(5)* starts *QEMU* as a daemon and then pins the 4 KVM threads (one for each emulated CPU core) to host CPUs 2, 3, 4 and 5. IO threads and other QEMU worker threads are pinned
to host CPUs 0 and 1.

In this example the host kernel has been configured to isolate cores 2, 3, 4 & 5 so they can be solely utilised by *QEMU*.\

::

	[Unit]
	Description=QEMU virtual machine
	After=network.target netctl@br0.service

	[Service]
	CPUSchedulingPolicy=rr

	Type=forking
	PIDFile=/run/qemu_ex.pid

	Environment=QEMU_AUDIO_DRV=pa

	ExecStart=/usr/bin/qemu-system-x86_64 -name example-qemu-machine,debug-threads=on -daemonize -pidfile /run/qemu_ex.pid -monitor unix:/tmp/qemu_ex.sock,server,nowait -smp cores=4,threads=1,sockets=1 ...
	ExecStartPost=/bin/sh -c 'exec /usr/bin/qemu-affinity $MAINPID -p 0-1 -i *:0-1 -q 0-1 -w *:0-1 -k 2 3 4 5'

	ExecStop=/bin/sh -c 'while test -d /proc/$MAINPID; do /usr/bin/echo system_powerdown | /usr/bin/socat - UNIX-CONNECT:/tmp/qemu_ex.sock; sleep 60; done'
	TimeoutStopSec=1m

	[Install]
	WantedBy=multi-user.target



