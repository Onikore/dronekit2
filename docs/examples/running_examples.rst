.. _running_examples_top:

====================
Running the Examples
====================

General instructions for running the `example source code <https://github.com/Onikore/dronekit2/tree/main/examples>`_ are given below. More explicit instructions are provided within the documentation for each example (and within the examples themselves by passing the ``-h`` (help) command line argument).

.. tip::

    Several examples try to auto-launch a simulator via the ``dronekit-sitl`` pip package by
    default if no ``--connect`` argument is given. That package is dead (see :ref:`sitl_setup`),
    so this auto-launch no longer works - pass ``--connect`` explicitly, pointing at a SITL
    instance you started yourself (see :ref:`sitl_setup`) or a real vehicle, using the
    :ref:`connection string <get_started_connect_string>` syntax.

To run the examples:

#. :ref:`Install DroneKit-Python <installing_dronekit>` if you have not already done so! Set up an ArduPilot SITL instance (see :ref:`sitl_setup`) if you want to test against simulated vehicles.

#. Get the DroneKit-Python example source code onto your local machine. The easiest way to do this
   is to clone the **dronekit2** repository from Github.

   On the command prompt enter:

   .. code-block:: bash

       git clone https://github.com/Onikore/dronekit2.git



#. Navigate to the example you wish to run (or specify the full path in the next step). The examples are all stored in
   subdirectories of **dronekit2/examples/**.

   For example, to run the :ref:`vehicle_state <example-vehicle-state>` example, you would navigate as shown:

   .. code-block:: bash

       cd dronekit2/examples/vehicle_state/


#. Start the example as shown:

   * To connect to a simulator started/managed by the script:
   
     .. code-block:: bash

         python vehicle_state.py

   * To connect to a specific vehicle, pass its :ref:`connection string <get_started_connect_string>` via the ``connect`` argument. 
     For example, to run the example on Solo you would use the following command:
   
     .. code-block:: bash

         python vehicle_state.py --connect udpin:0.0.0.0:14550


.. warning:: 

    Propellers should be removed before testing examples indoors (on real vehicles). 
