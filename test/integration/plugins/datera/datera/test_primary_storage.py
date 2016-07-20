import logging
import random
import XenAPI
# All tests inherit from cloudstackTestCase
from marvin.cloudstackTestCase import cloudstackTestCase

# Import Integration Libraries

from marvin.lib.base import ServiceOffering, StoragePool

# common - commonly used methods for all tests are listed here
from marvin.lib.common import (get_domain, get_zone,
                               list_hosts, list_clusters,
                               list_storage_pools)

# utils - utility classes for common cleanup, external library wrappers, etc.
from marvin.lib.utils import cleanup_resources

from dfs_sdk import DateraApi


class TestData:
    account = "account"
    capacityBytes = "capacitybytes"
    capacityIops = "capacityiops"
    clusterId = "clusterId"
    computeOffering = "computeoffering"
    displayText = "displaytext"
    diskSize = "disksize"
    domainId = "domainId"
    hypervisor = "hypervisor"
    login = "login"
    mvip = "mvip"
    name = "name"
    newHost = "newHost"
    newHostDisplayName = "newHostDisplayName"
    osType = "ostype"
    password = "password"
    podId = "podid"
    port = "port"
    primaryStorage = "primarystorage"
    primaryStorage2 = "primarystorage2"
    primaryStorage3 = "primarystorage3"
    primaryStorage4 = "primarystorage4"
    primaryStorage5 = "primaryStorage5"
    provider = "provider"
    scope = "scope"
    Datera = "Datera"
    storageTag = "Datera_1"
    storageTag2 = "datera_2"
    tags = "tags"
    url = "url"
    path = "path"
    urlOfNewHost = "urlOfNewHost"
    user = "user"
    username = "username"
    virtualMachine = "virtualmachine"
    volume_1 = "volume_1"
    xenServer = "xenserver"
    zoneId = "zoneid"
    clusterName = "clusterName"
    hostName = "hostname"

    def __init__(self):
        self.datear_url = (
            "mgmtIP=172.19.2.214;mgmtPort=7718;" +
            "mgmtUserName=admin;mgmtPassword=password;" +
            "replica=3;networkPoolName=default"),
        self.datear_url_without_replica = (
            "mgmtIP=172.19.1.214;mgmtPort=7718;" +
            "mgmtUserName=admin;mgmtPassword=password;" +
            "networkPoolName=default"),
        self.datear_url_without_netpool = (
            "mgmtIP=172.19.2.214;mgmtPort=7718;" +
            "mgmtUserName=admin;mgmtPassword=password;" +
            "replica=3"),
        self.testdata = {
            TestData.Datera: {
                TestData.mvip: "172.19.2.214",
                TestData.login: "admin",
                TestData.password: "password",
            },
            TestData.xenServer: {
                TestData.username: "root",
                TestData.password: "maple"
            },
            TestData.primaryStorage: {
                TestData.name: "datera-%d" % random.randint(0, 100),
                TestData.scope: "CLUSTER",
                TestData.url: self.datear_url[0],
                TestData.provider: "DateraShared",
                TestData.tags: TestData.storageTag,
                TestData.capacityIops: 5000,
                TestData.capacityBytes: 1073741824,
                TestData.hypervisor: "XenServer",
                TestData.podId: 1
            },
            TestData.primaryStorage2: {
                TestData.name: "Datera-%d" % random.randint(0, 100),
                TestData.scope: "CLUSTER",
                TestData.url: self.datear_url[0],
                TestData.provider: "DateraShared",
                TestData.tags: TestData.storageTag,
                TestData.capacityIops: 5000,
                TestData.capacityBytes: 125000000000000,
                TestData.hypervisor: "XenServer",
                TestData.podId: 1
            },
            TestData.primaryStorage3: {
                TestData.name: "Datera-%d" % random.randint(0, 100),
                TestData.scope: "CLUSTER",
                TestData.url: self.datear_url_without_replica[0],
                TestData.provider: "DateraShared",
                TestData.tags: TestData.storageTag,
                TestData.capacityIops: 5000,
                TestData.capacityBytes: 1073741824,
                TestData.hypervisor: "XenServer",
                TestData.podId: 1
            },
            TestData.primaryStorage4: {
                TestData.name: "Datera-%d" % random.randint(0, 100),
                TestData.scope: "CLUSTER",
                TestData.url: self.datear_url_without_netpool[0],
                TestData.provider: "DateraShared",
                TestData.tags: TestData.storageTag,
                TestData.capacityIops: 5000,
                TestData.capacityBytes: 1073741824,
                TestData.hypervisor: "XenServer",
                TestData.podId: 1
            },
            TestData.primaryStorage5: {
                TestData.name: "datera-%d" % random.randint(0, 100),
                TestData.scope: "CLUSTER",
                TestData.url: self.datear_url[0],
                TestData.provider: "DateraShared",
                TestData.tags: TestData.storageTag,
                TestData.capacityIops: 0,
                TestData.capacityBytes: 1073741824,
                TestData.hypervisor: "XenServer",
                TestData.podId: 1
            },
            TestData.computeOffering: {
                TestData.name: "DATERA",
                TestData.displayText: (
                    "DATERA (Min IOPS = 10,000; Max IOPS = 15,000)"),
                "cpunumber": 1,
                "cpuspeed": 100,
                "memory": 128,
                "storagetype": "shared",
                "customizediops": False,
                "miniops": "10000",
                "maxiops": "15000",
                "hypervisorsnapshotreserve": 200,
                TestData.tags: TestData.storageTag
            },
            TestData.osType: "CentOS 5.6(64-bit) no GUI (XenServer)",
            TestData.zoneId: 1,
            TestData.clusterId: 1,
            TestData.domainId: 1,
            TestData.url: "172.19.175.174",
            TestData.clusterName: "Cluster-Xen",
            TestData.hostName: "tlx167.tlx.daterainc.com"
        }


class TestPrimaryStorage(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        # Set up API client
        testclient = super(TestPrimaryStorage, cls).getClsTestClient()
        cls.apiClient = testclient.getApiClient()
        cls.dbConnection = testclient.getDbConnection()
        cls.services = testclient.getParsedTestDataConfig()
        cls.testdata = TestData().testdata
        cls.zone = get_zone(
            cls.apiClient, zone_id=cls.testdata[TestData.zoneId])
        for cluster in list_clusters(cls.apiClient):
            if cluster.name == cls.testdata[TestData.clusterName]:
                cls.cluster = cluster
        cls.domain = get_domain(cls.apiClient, cls.testdata[TestData.domainId])
        cls.xs_pool_master_ip = list_hosts(
            cls.apiClient, clusterid=cls.cluster.id)
        for host in cls.xs_pool_master_ip:
            if host.name == cls.testdata[TestData.hostName]:
                cls.xs_pool_master_ip = host.ipaddress
        host_ip = "https://" + cls.xs_pool_master_ip
        cls.xen_session = XenAPI.Session(host_ip)
        xenserver = cls.testdata[TestData.xenServer]
        cls.xen_session.xenapi.login_with_password(
            xenserver[TestData.username], xenserver[TestData.password])
        datera = cls.testdata[TestData.Datera]
        cls.datera_api = DateraApi(
            username=datera[TestData.login],
            password=datera[TestData.password],
            hostname=datera[TestData.mvip])

        cls.compute_offering = ServiceOffering.create(
            cls.apiClient,
            cls.testdata[TestData.computeOffering]
        )

        cls._cleanup = [cls.compute_offering]

    @classmethod
    def tearDownClass(cls):
        try:
            cleanup_resources(cls.apiClient, cls._cleanup)
        except Exception as e:
            logging.debug("Exception in tearDownClass(cls): %s" % e)

    def setUp(self):
        self.virtual_machine = None
        self.cleanup = []

    def tearDown(self):
        try:
            primarystorage = self.testdata[TestData.primaryStorage]
            if self.virtual_machine is not None:
                self.virtual_machine.delete(self.apiClient, True)

            cleanup_resources(self.apiClient, self.cleanup)
            flag = 0
            for item in self.datera_api.app_instances.list():
                if item['name'] == primarystorage[TestData.name]:
                    flag = 1
            if flag > 0:
                raise Exception('app instance not deleted.')
        except Exception as e:
            logging.debug("Exception in tearDown(self): %s" % e)
            raise

    def test01_primary_storage_positive(self):
        primarystorage = self.testdata[TestData.primaryStorage]
        primary_storage = StoragePool.create(
            self.apiClient,
            primarystorage,
            scope=primarystorage[TestData.scope],
            zoneid=self.zone.id,
            clusterid=self.cluster.id,
            provider=primarystorage[TestData.provider],
            tags=primarystorage[TestData.tags],
            capacityiops=primarystorage[TestData.capacityIops],
            capacitybytes=primarystorage[TestData.capacityBytes],
            hypervisor=primarystorage[TestData.hypervisor]
        )

        self.cleanup.append(primary_storage)
        primary_storage_name = "cloudstack-" + primary_storage.id
        self.assertEqual(
            any(primary_storage_name == app_instance['name']
                for app_instance in self.datera_api.app_instances.list()),
            True, "app instance not created")
        primary_storage_url = primarystorage[TestData.url]
        self._verify_attributes(
            primary_storage.id, primary_storage_url)

    def test02_primary_storage_negative(self):
        primarystorage2 = self.testdata[TestData.primaryStorage2]
        primary_storage2 = StoragePool.create(
            self.apiClient,
            primarystorage2,
            scope=primarystorage2[TestData.scope],
            zoneid=self.zone.id,
            clusterid=self.cluster.id,
            provider=primarystorage2[TestData.provider],
            tags=primarystorage2[TestData.tags],
            capacityiops=primarystorage2[TestData.capacityIops],
            capacitybytes=primarystorage2[TestData.capacityBytes],
            hypervisor=primarystorage2[TestData.hypervisor]
        )

        self.cleanup.append(primary_storage2)
        primary_storage_name = "cloudstack-" + primary_storage2.id
        self.assertEqual(
            any(primary_storage_name == app_instance['name']
                for app_instance in self.datera_api.app_instances.list()),
            True, "app instance not created")

        primary_storage_url = primarystorage2[TestData.url]

        self._verify_attributes(
            primary_storage2.id, primary_storage_url)

    def test03_primary_storage_without_replica(self):
        primarystorage3 = self.testdata[TestData.primaryStorage3]

        primary_storage3 = StoragePool.create(
            self.apiClient,
            primarystorage3,
            scope=primarystorage3[TestData.scope],
            zoneid=self.zone.id,
            clusterid=self.cluster.id,
            provider=primarystorage3[TestData.provider],
            tags=primarystorage3[TestData.tags],
            capacityiops=primarystorage3[TestData.capacityIops],
            capacitybytes=primarystorage3[TestData.capacityBytes],
            hypervisor=primarystorage3[TestData.hypervisor]
        )

        self.cleanup.append(primary_storage3)
        primary_storage_name = "cloudstack-" + primary_storage3.id
        self.assertEqual(
            any(primary_storage_name == app_instance['name']
                for app_instance in self.datera_api.app_instances.list()),
            True, "app instance not created")

        primary_storage_url = primarystorage3[TestData.url]

        self._verify_attributes(
            primary_storage3.id, primary_storage_url)

    def test11_primary_storage_without_netpool(self):
        primarystorage4 = self.testdata[TestData.primaryStorage4]

        primary_storage4 = StoragePool.create(
            self.apiClient,
            primarystorage4,
            scope=primarystorage4[TestData.scope],
            zoneid=self.zone.id,
            clusterid=self.cluster.id,
            provider=primarystorage4[TestData.provider],
            tags=primarystorage4[TestData.tags],
            capacityiops=primarystorage4[TestData.capacityIops],
            capacitybytes=primarystorage4[TestData.capacityBytes],
            hypervisor=primarystorage4[TestData.hypervisor]
        )

        self.cleanup.append(primary_storage4)
        primary_storage_name = "cloudstack-" + primary_storage4.id
        self.assertEqual(
            any(primary_storage_name == app_instance['name']
                for app_instance in self.datera_api.app_instances.list()),
            True, "app instance not created")

        primary_storage_url = primarystorage4[TestData.url]

        self._verify_attributes(
            primary_storage4.id, primary_storage_url)

    def test12_primary_storage_with_zero_iops(self):
        primarystorage5 = self.testdata[TestData.primaryStorage5]

        primary_storage5 = StoragePool.create(
            self.apiClient,
            primarystorage5,
            scope=primarystorage5[TestData.scope],
            zoneid=self.zone.id,
            clusterid=self.cluster.id,
            provider=primarystorage5[TestData.provider],
            tags=primarystorage5[TestData.tags],
            capacityiops=primarystorage5[TestData.capacityIops],
            capacitybytes=primarystorage5[TestData.capacityBytes],
            hypervisor=primarystorage5[TestData.hypervisor]
        )

        self.cleanup.append(primary_storage5)
        primary_storage_name = "cloudstack-" + primary_storage5.id
        self.assertEqual(
            any(primary_storage_name == app_instance['name']
                for app_instance in self.datera_api.app_instances.list()),
            True, "app instance not created")

        primary_storage_url = primarystorage5[TestData.url]

        self._verify_attributes(
            primary_storage5.id, primary_storage_url)

    def _verify_attributes(self, primarystorage_id, primary_storage_url):
        #Cloudstack Primary storage pool
        storage_pools_response = list_storage_pools(
            self.apiClient, id=primarystorage_id)
        storage_pools_response = storage_pools_response[0]
        storage_pools_response_type = storage_pools_response.type
        storage_pools_response_iqn = storage_pools_response.path
        storage_pools_response_disk = storage_pools_response.disksizetotal
        storage_pools_response_ipaddress = storage_pools_response.ipaddress
        storage_pools_response_state = storage_pools_response.state
        storage_pools_response_iops = storage_pools_response.capacityiops

        self.assertEqual(
            storage_pools_response_type, "IscsiLUN",
            "Failed to create IscsiLUN")

        self.assertEqual(
            storage_pools_response_state, "Up",
            "Primary storage status is down")

        # Datera app instances
        datera_primarystorage_name = "cloudstack-" + primarystorage_id
        for instance in self.datera_api.app_instances.list():
            if instance['name'] == datera_primarystorage_name:
                app_instance_response = instance
        app_instance_response_iqn = (
            app_instance_response['storage_instances']
            ['storage-1']['access']['iqn'])
        app_instance_response_ipaddress = (
            app_instance_response['storage_instances']
            ['storage-1']['access']['ips'])
        app_instance_response_op_state = (
            app_instance_response['storage_instances']
            ['storage-1']['volumes']['volume-1']['op_state'])
        app_instance_response_disk = (
            app_instance_response['storage_instances']
            ['storage-1']['volumes']['volume-1']['size'] * 1073741824)
        app_instance_response_iops = (
            app_instance_response['storage_instances']
            ['storage-1']['volumes']['volume-1'])
        app_instance_response_replica = (
            app_instance_response['storage_instances']
            ['storage-1']['volumes']['volume-1']['replica_count'])
        app_instance_response_ippool = (
            app_instance_response['storage_instances']
            ['storage-1']['ip_pool'])

        cs_replica = [data for data in primary_storage_url.split(";")
                      if data.startswith('replica')]
        cs_netPool = [data for data in primary_storage_url.split(";")
                      if data.startswith('networkPoolName')]

        if cs_replica:
            replica_count = ''.join(cs_replica).split("=")[1]

            self.assertEqual(
                int(replica_count),
                int(app_instance_response_replica),
                "Incorrect replicas count")
        if not cs_replica:
            self.assertEqual(
                int(3),
                int(app_instance_response_replica),
                "Incorrect replicas count")

        if cs_netPool:
            cs_netPool = ''.join(cs_netPool).split("=")[1]
            self.assertEqual(
                app_instance_response_ippool.split('/')[2],
                cs_netPool,
                "Incorrect networkPoolName")

        if not cs_netPool:
            self.assertEqual(
                app_instance_response_ippool.split('/')[2],
                'default',
                "Incorrect networkPool Name")
        # Verify in sql database
        command = (
            "select status,id  from storage_pool where uuid='" +
            primarystorage_id + "'")
        sql_result = self.dbConnection.execute(command)
        self.assertEqual(
            sql_result[0][0], 'Up',
            "Priamry storage not added in database")

        command2 = (
            "select * from storage_pool_details where pool_id='" +
            str(sql_result[0][1]) + "'")

        sql_result1 = self.dbConnection.execute(command2)
        flag = 0
        for data in sql_result1:
            for record in data:
                if record == datera_primarystorage_name:
                    flag = 1
        self.assertEqual(
            flag, 1,
            "Priamry storage not added in database")

        self.assertEqual(
            app_instance_response_op_state, "available",
            "datera app instance is down")

        # xen server details
        for key, value in self.xen_session.xenapi.SR.get_all_records().items():
            if value['name_description'] == primarystorage_id:
                xen_server_response = value

        #xen_server_response_iqn = xen_server_response['name_description']
        xen_server_response_type = xen_server_response['type']
        xen_server_physical_size = xen_server_response['physical_size']

        if (storage_pools_response_ipaddress not in
                app_instance_response_ipaddress):
            self.assert_(False, "Storage ip address are different")

        self.assertEqual(
            xen_server_response_type, "lvmoiscsi",
            "Failed to craete lvmoiscsi on xen server")

        self.assertEqual(
            storage_pools_response_iqn.split("/")[1],
            app_instance_response_iqn,
            "Iqn values mismatch")

        self.assertEqual(
            app_instance_response_disk,
            storage_pools_response_disk,
            "Disk sizes are different")

        self.assertEqual(
            int(xen_server_physical_size) + 12582912,
            storage_pools_response_disk,
            "Disk sizes are not same in xen and cloudsatck")

        if "performance_policy" in app_instance_response_iops:
            datera_iops =  (
                app_instance_response_iops["performance_policy"]
                ["total_iops_max"])
            self.assertEqual(
                storage_pools_response_iops,
                datera_iops,
                "IOPS values are incorrect")
