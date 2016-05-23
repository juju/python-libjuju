
from libjuju.facade import Type, ReturnMapping
                  
class Action(Type):
    _toSchema = {'name': 'name', 'receiver': 'receiver', 'parameters': 'parameters', 'tag': 'tag'}
    _toPy = {'name': 'name', 'receiver': 'receiver', 'parameters': 'parameters', 'tag': 'tag'}
    def __init__(self, name, receiver, parameters, tag):
        '''
        name : str
        receiver : str
        parameters : typing.Mapping[str, typing.Any]
        tag : str
        '''
        self.name = name
        self.receiver = receiver
        self.parameters = parameters
        self.tag = tag


class ActionResult(Type):
    _toSchema = {'action': 'action', 'output': 'output', 'enqueued': 'enqueued', 'status': 'status', 'message': 'message', 'started': 'started', 'completed': 'completed', 'error': 'error'}
    _toPy = {'action': 'action', 'output': 'output', 'enqueued': 'enqueued', 'status': 'status', 'message': 'message', 'started': 'started', 'completed': 'completed', 'error': 'error'}
    def __init__(self, action, output, enqueued, status, message, started, completed, error):
        '''
        action : ~Action
        output : typing.Mapping[str, typing.Any]
        enqueued : str
        status : str
        message : str
        started : str
        completed : str
        error : ~Error
        '''
        self.action = action
        self.output = output
        self.enqueued = enqueued
        self.status = status
        self.message = message
        self.started = started
        self.completed = completed
        self.error = error


class Actions(Type):
    _toSchema = {'actions': 'actions'}
    _toPy = {'actions': 'actions'}
    def __init__(self, actions):
        '''
        actions : typing.Sequence[~Action]
        '''
        self.actions = actions


class ActionsByName(Type):
    _toSchema = {'name': 'name', 'actions': 'actions', 'error': 'error'}
    _toPy = {'name': 'name', 'actions': 'actions', 'error': 'error'}
    def __init__(self, name, actions, error):
        '''
        name : str
        actions : typing.Sequence[~ActionResult]
        error : ~Error
        '''
        self.name = name
        self.actions = actions
        self.error = error


class ActionsByReceiver(Type):
    _toSchema = {'receiver': 'receiver', 'actions': 'actions', 'error': 'error'}
    _toPy = {'receiver': 'receiver', 'actions': 'actions', 'error': 'error'}
    def __init__(self, receiver, actions, error):
        '''
        receiver : str
        actions : typing.Sequence[~ActionResult]
        error : ~Error
        '''
        self.receiver = receiver
        self.actions = actions
        self.error = error


class Entity(Type):
    _toSchema = {'tag': 'Tag'}
    _toPy = {'Tag': 'tag'}
    def __init__(self, tag):
        '''
        tag : str
        '''
        self.tag = tag


class Error(Type):
    _toSchema = {'info': 'Info', 'code': 'Code', 'message': 'Message'}
    _toPy = {'Info': 'info', 'Code': 'code', 'Message': 'message'}
    def __init__(self, info, code, message):
        '''
        info : ~ErrorInfo
        code : str
        message : str
        '''
        self.info = info
        self.code = code
        self.message = message


class ErrorInfo(Type):
    _toSchema = {'macaroonpath': 'MacaroonPath', 'macaroon': 'Macaroon'}
    _toPy = {'Macaroon': 'macaroon', 'MacaroonPath': 'macaroonpath'}
    def __init__(self, macaroon, macaroonpath):
        '''
        macaroon : ~Macaroon
        macaroonpath : str
        '''
        self.macaroon = macaroon
        self.macaroonpath = macaroonpath


class Macaroon(Type):
    _toSchema = {'caveats': 'caveats', 'id_': 'id', 'data': 'data', 'location': 'location', 'sig': 'sig'}
    _toPy = {'caveats': 'caveats', 'id': 'id_', 'data': 'data', 'location': 'location', 'sig': 'sig'}
    def __init__(self, caveats, id_, data, location, sig):
        '''
        caveats : typing.Sequence[~caveat]
        id_ : ~packet
        data : typing.Sequence[int]
        location : ~packet
        sig : typing.Sequence[int]
        '''
        self.caveats = caveats
        self.id_ = id_
        self.data = data
        self.location = location
        self.sig = sig


class ServiceCharmActionsResult(Type):
    _toSchema = {'servicetag': 'servicetag', 'actions': 'actions', 'error': 'error'}
    _toPy = {'servicetag': 'servicetag', 'actions': 'actions', 'error': 'error'}
    def __init__(self, servicetag, actions, error):
        '''
        servicetag : str
        actions : ~Actions
        error : ~Error
        '''
        self.servicetag = servicetag
        self.actions = actions
        self.error = error


class caveat(Type):
    _toSchema = {'location': 'location', 'caveatid': 'caveatId', 'verificationid': 'verificationId'}
    _toPy = {'verificationId': 'verificationid', 'location': 'location', 'caveatId': 'caveatid'}
    def __init__(self, verificationid, location, caveatid):
        '''
        verificationid : ~packet
        location : ~packet
        caveatid : ~packet
        '''
        self.verificationid = verificationid
        self.location = location
        self.caveatid = caveatid


class packet(Type):
    _toSchema = {'start': 'start', 'totallen': 'totalLen', 'headerlen': 'headerLen'}
    _toPy = {'start': 'start', 'headerLen': 'headerlen', 'totalLen': 'totallen'}
    def __init__(self, start, headerlen, totallen):
        '''
        start : int
        headerlen : int
        totallen : int
        '''
        self.start = start
        self.headerlen = headerlen
        self.totallen = totallen


class AgentGetEntitiesResult(Type):
    _toSchema = {'containertype': 'ContainerType', 'life': 'Life', 'error': 'Error', 'jobs': 'Jobs'}
    _toPy = {'Life': 'life', 'Error': 'error', 'ContainerType': 'containertype', 'Jobs': 'jobs'}
    def __init__(self, life, error, containertype, jobs):
        '''
        life : str
        error : ~Error
        containertype : str
        jobs : typing.Sequence[str]
        '''
        self.life = life
        self.error = error
        self.containertype = containertype
        self.jobs = jobs


class EntityPassword(Type):
    _toSchema = {'password': 'Password', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Password': 'password'}
    def __init__(self, tag, password):
        '''
        tag : str
        password : str
        '''
        self.tag = tag
        self.password = password


class ErrorResult(Type):
    _toSchema = {'info': 'Info', 'code': 'Code', 'message': 'Message'}
    _toPy = {'Info': 'info', 'Code': 'code', 'Message': 'message'}
    def __init__(self, info, code, message):
        '''
        info : ~ErrorInfo
        code : str
        message : str
        '''
        self.info = info
        self.code = code
        self.message = message


class Delta(Type):
    _toSchema = {'removed': 'Removed'}
    _toPy = {'Removed': 'removed'}
    def __init__(self, removed):
        '''
        removed : bool
        '''
        self.removed = removed


class AnnotationsGetResult(Type):
    _toSchema = {'error': 'Error', 'entitytag': 'EntityTag', 'annotations': 'Annotations'}
    _toPy = {'Error': 'error', 'Annotations': 'annotations', 'EntityTag': 'entitytag'}
    def __init__(self, error, entitytag, annotations):
        '''
        error : ~ErrorResult
        entitytag : str
        annotations : typing.Mapping[str, str]
        '''
        self.error = error
        self.entitytag = entitytag
        self.annotations = annotations


class EntityAnnotations(Type):
    _toSchema = {'annotations': 'Annotations', 'entitytag': 'EntityTag'}
    _toPy = {'Annotations': 'annotations', 'EntityTag': 'entitytag'}
    def __init__(self, entitytag, annotations):
        '''
        entitytag : str
        annotations : typing.Mapping[str, str]
        '''
        self.entitytag = entitytag
        self.annotations = annotations


class BackupsMetadataResult(Type):
    _toSchema = {'version': 'Version', 'started': 'Started', 'notes': 'Notes', 'finished': 'Finished', 'machine': 'Machine', 'hostname': 'Hostname', 'caprivatekey': 'CAPrivateKey', 'checksumformat': 'ChecksumFormat', 'id_': 'ID', 'size': 'Size', 'stored': 'Stored', 'checksum': 'Checksum', 'model': 'Model', 'cacert': 'CACert'}
    _toPy = {'Hostname': 'hostname', 'Model': 'model', 'Version': 'version', 'Checksum': 'checksum', 'Stored': 'stored', 'ID': 'id_', 'Machine': 'machine', 'Size': 'size', 'Started': 'started', 'Notes': 'notes', 'Finished': 'finished', 'CACert': 'cacert', 'ChecksumFormat': 'checksumformat', 'CAPrivateKey': 'caprivatekey'}
    def __init__(self, hostname, model, version, checksum, stored, id_, machine, size, started, notes, finished, cacert, checksumformat, caprivatekey):
        '''
        hostname : str
        model : str
        version : ~Number
        checksum : str
        stored : str
        id_ : str
        machine : str
        size : int
        started : str
        notes : str
        finished : str
        cacert : str
        checksumformat : str
        caprivatekey : str
        '''
        self.hostname = hostname
        self.model = model
        self.version = version
        self.checksum = checksum
        self.stored = stored
        self.id_ = id_
        self.machine = machine
        self.size = size
        self.started = started
        self.notes = notes
        self.finished = finished
        self.cacert = cacert
        self.checksumformat = checksumformat
        self.caprivatekey = caprivatekey


class Number(Type):
    _toSchema = {'major': 'Major', 'patch': 'Patch', 'build': 'Build', 'minor': 'Minor', 'tag': 'Tag'}
    _toPy = {'Build': 'build', 'Minor': 'minor', 'Tag': 'tag', 'Patch': 'patch', 'Major': 'major'}
    def __init__(self, build, minor, tag, patch, major):
        '''
        build : int
        minor : int
        tag : str
        patch : int
        major : int
        '''
        self.build = build
        self.minor = minor
        self.tag = tag
        self.patch = patch
        self.major = major


class Block(Type):
    _toSchema = {'tag': 'tag', 'id_': 'id', 'message': 'message', 'type_': 'type'}
    _toPy = {'id': 'id_', 'message': 'message', 'type': 'type_', 'tag': 'tag'}
    def __init__(self, id_, message, type_, tag):
        '''
        id_ : str
        message : str
        type_ : str
        tag : str
        '''
        self.id_ = id_
        self.message = message
        self.type_ = type_
        self.tag = tag


class BlockResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~Block
        '''
        self.error = error
        self.result = result


class AddMachineParams(Type):
    _toSchema = {'nonce': 'Nonce', 'placement': 'Placement', 'constraints': 'Constraints', 'addrs': 'Addrs', 'disks': 'Disks', 'jobs': 'Jobs', 'instanceid': 'InstanceId', 'series': 'Series', 'containertype': 'ContainerType', 'parentid': 'ParentId', 'hardwarecharacteristics': 'HardwareCharacteristics'}
    _toPy = {'InstanceId': 'instanceid', 'ParentId': 'parentid', 'ContainerType': 'containertype', 'Constraints': 'constraints', 'Nonce': 'nonce', 'Series': 'series', 'Disks': 'disks', 'HardwareCharacteristics': 'hardwarecharacteristics', 'Placement': 'placement', 'Jobs': 'jobs', 'Addrs': 'addrs'}
    def __init__(self, constraints, parentid, containertype, addrs, nonce, series, instanceid, disks, placement, jobs, hardwarecharacteristics):
        '''
        constraints : ~Value
        parentid : str
        containertype : str
        addrs : typing.Sequence[~Address]
        nonce : str
        series : str
        instanceid : str
        disks : typing.Sequence[~Constraints]
        placement : ~Placement
        jobs : typing.Sequence[str]
        hardwarecharacteristics : ~HardwareCharacteristics
        '''
        self.constraints = constraints
        self.parentid = parentid
        self.containertype = containertype
        self.addrs = addrs
        self.nonce = nonce
        self.series = series
        self.instanceid = instanceid
        self.disks = disks
        self.placement = placement
        self.jobs = jobs
        self.hardwarecharacteristics = hardwarecharacteristics


class AddMachinesResult(Type):
    _toSchema = {'machine': 'Machine', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Machine': 'machine'}
    def __init__(self, error, machine):
        '''
        error : ~Error
        machine : str
        '''
        self.error = error
        self.machine = machine


class Address(Type):
    _toSchema = {'spacename': 'SpaceName', 'value': 'Value', 'scope': 'Scope', 'type_': 'Type'}
    _toPy = {'Type': 'type_', 'Value': 'value', 'Scope': 'scope', 'SpaceName': 'spacename'}
    def __init__(self, type_, value, scope, spacename):
        '''
        type_ : str
        value : str
        scope : str
        spacename : str
        '''
        self.type_ = type_
        self.value = value
        self.scope = scope
        self.spacename = spacename


class Binary(Type):
    _toSchema = {'number': 'Number', 'arch': 'Arch', 'series': 'Series'}
    _toPy = {'Series': 'series', 'Arch': 'arch', 'Number': 'number'}
    def __init__(self, series, number, arch):
        '''
        series : str
        number : ~Number
        arch : str
        '''
        self.series = series
        self.number = number
        self.arch = arch


class BundleChangesChange(Type):
    _toSchema = {'requires': 'requires', 'id_': 'id', 'method': 'method', 'args': 'args'}
    _toPy = {'requires': 'requires', 'id': 'id_', 'method': 'method', 'args': 'args'}
    def __init__(self, requires, id_, method, args):
        '''
        requires : typing.Sequence[str]
        id_ : str
        method : str
        args : typing.Sequence[typing.Any]
        '''
        self.requires = requires
        self.id_ = id_
        self.method = method
        self.args = args


class Constraints(Type):
    _toSchema = {'size': 'Size', 'pool': 'Pool', 'count': 'Count'}
    _toPy = {'Count': 'count', 'Pool': 'pool', 'Size': 'size'}
    def __init__(self, count, pool, size):
        '''
        count : int
        pool : str
        size : int
        '''
        self.count = count
        self.pool = pool
        self.size = size


class DetailedStatus(Type):
    _toSchema = {'info': 'Info', 'version': 'Version', 'status': 'Status', 'since': 'Since', 'kind': 'Kind', 'data': 'Data', 'life': 'Life'}
    _toPy = {'Info': 'info', 'Data': 'data', 'Kind': 'kind', 'Version': 'version', 'Life': 'life', 'Status': 'status', 'Since': 'since'}
    def __init__(self, data, kind, version, life, info, status, since):
        '''
        data : typing.Mapping[str, typing.Any]
        kind : str
        version : str
        life : str
        info : str
        status : str
        since : str
        '''
        self.data = data
        self.kind = kind
        self.version = version
        self.life = life
        self.info = info
        self.status = status
        self.since = since


class EndpointStatus(Type):
    _toSchema = {'servicename': 'ServiceName', 'name': 'Name', 'subordinate': 'Subordinate', 'role': 'Role'}
    _toPy = {'Name': 'name', 'Role': 'role', 'ServiceName': 'servicename', 'Subordinate': 'subordinate'}
    def __init__(self, name, role, servicename, subordinate):
        '''
        name : str
        role : str
        servicename : str
        subordinate : bool
        '''
        self.name = name
        self.role = role
        self.servicename = servicename
        self.subordinate = subordinate


class EntityStatus(Type):
    _toSchema = {'info': 'Info', 'status': 'Status', 'data': 'Data', 'since': 'Since'}
    _toPy = {'Info': 'info', 'Data': 'data', 'Status': 'status', 'Since': 'since'}
    def __init__(self, info, data, status, since):
        '''
        info : str
        data : typing.Mapping[str, typing.Any]
        status : str
        since : str
        '''
        self.info = info
        self.data = data
        self.status = status
        self.since = since


class HardwareCharacteristics(Type):
    _toSchema = {'arch': 'Arch', 'mem': 'Mem', 'cpucores': 'CpuCores', 'availabilityzone': 'AvailabilityZone', 'rootdisk': 'RootDisk', 'cpupower': 'CpuPower', 'tags': 'Tags'}
    _toPy = {'Mem': 'mem', 'CpuCores': 'cpucores', 'CpuPower': 'cpupower', 'RootDisk': 'rootdisk', 'Tags': 'tags', 'Arch': 'arch', 'AvailabilityZone': 'availabilityzone'}
    def __init__(self, mem, cpucores, cpupower, rootdisk, tags, arch, availabilityzone):
        '''
        mem : int
        cpucores : int
        cpupower : int
        rootdisk : int
        tags : typing.Sequence[str]
        arch : str
        availabilityzone : str
        '''
        self.mem = mem
        self.cpucores = cpucores
        self.cpupower = cpupower
        self.rootdisk = rootdisk
        self.tags = tags
        self.arch = arch
        self.availabilityzone = availabilityzone


class HostPort(Type):
    _toSchema = {'port': 'Port', 'address': 'Address'}
    _toPy = {'Port': 'port', 'Address': 'address'}
    def __init__(self, port, address):
        '''
        port : int
        address : ~Address
        '''
        self.port = port
        self.address = address


class MachineStatus(Type):
    _toSchema = {'agentstatus': 'AgentStatus', 'id_': 'Id', 'instancestatus': 'InstanceStatus', 'jobs': 'Jobs', 'hardware': 'Hardware', 'instanceid': 'InstanceId', 'series': 'Series', 'dnsname': 'DNSName', 'containers': 'Containers', 'wantsvote': 'WantsVote', 'hasvote': 'HasVote'}
    _toPy = {'Id': 'id_', 'HasVote': 'hasvote', 'Series': 'series', 'AgentStatus': 'agentstatus', 'Containers': 'containers', 'InstanceId': 'instanceid', 'WantsVote': 'wantsvote', 'Hardware': 'hardware', 'InstanceStatus': 'instancestatus', 'Jobs': 'jobs', 'DNSName': 'dnsname'}
    def __init__(self, id_, hardware, series, instancestatus, instanceid, containers, wantsvote, hasvote, dnsname, jobs, agentstatus):
        '''
        id_ : str
        hardware : str
        series : str
        instancestatus : ~DetailedStatus
        instanceid : str
        containers : typing.Mapping[str, ~MachineStatus]
        wantsvote : bool
        hasvote : bool
        dnsname : str
        jobs : typing.Sequence[str]
        agentstatus : ~DetailedStatus
        '''
        self.id_ = id_
        self.hardware = hardware
        self.series = series
        self.instancestatus = instancestatus
        self.instanceid = instanceid
        self.containers = containers
        self.wantsvote = wantsvote
        self.hasvote = hasvote
        self.dnsname = dnsname
        self.jobs = jobs
        self.agentstatus = agentstatus


class MeterStatus(Type):
    _toSchema = {'message': 'Message', 'color': 'Color'}
    _toPy = {'Color': 'color', 'Message': 'message'}
    def __init__(self, color, message):
        '''
        color : str
        message : str
        '''
        self.color = color
        self.message = message


class ModelUserInfo(Type):
    _toSchema = {'lastconnection': 'lastconnection', 'displayname': 'displayname', 'access': 'access', 'user': 'user'}
    _toPy = {'lastconnection': 'lastconnection', 'displayname': 'displayname', 'access': 'access', 'user': 'user'}
    def __init__(self, lastconnection, displayname, access, user):
        '''
        lastconnection : str
        displayname : str
        access : str
        user : str
        '''
        self.lastconnection = lastconnection
        self.displayname = displayname
        self.access = access
        self.user = user


class ModelUserInfoResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~ModelUserInfo
        '''
        self.error = error
        self.result = result


class Placement(Type):
    _toSchema = {'directive': 'Directive', 'scope': 'Scope'}
    _toPy = {'Scope': 'scope', 'Directive': 'directive'}
    def __init__(self, scope, directive):
        '''
        scope : str
        directive : str
        '''
        self.scope = scope
        self.directive = directive


class RelationStatus(Type):
    _toSchema = {'endpoints': 'Endpoints', 'key': 'Key', 'id_': 'Id', 'scope': 'Scope', 'interface': 'Interface'}
    _toPy = {'Interface': 'interface', 'Key': 'key', 'Id': 'id_', 'Scope': 'scope', 'Endpoints': 'endpoints'}
    def __init__(self, interface, scope, id_, key, endpoints):
        '''
        interface : str
        scope : str
        id_ : int
        key : str
        endpoints : typing.Sequence[~EndpointStatus]
        '''
        self.interface = interface
        self.scope = scope
        self.id_ = id_
        self.key = key
        self.endpoints = endpoints


class ResolveCharmResult(Type):
    _toSchema = {'url': 'URL', 'error': 'Error'}
    _toPy = {'Error': 'error', 'URL': 'url'}
    def __init__(self, error, url):
        '''
        error : str
        url : ~URL
        '''
        self.error = error
        self.url = url


class ServiceStatus(Type):
    _toSchema = {'relations': 'Relations', 'units': 'Units', 'status': 'Status', 'life': 'Life', 'canupgradeto': 'CanUpgradeTo', 'exposed': 'Exposed', 'meterstatuses': 'MeterStatuses', 'charm': 'Charm', 'subordinateto': 'SubordinateTo'}
    _toPy = {'Exposed': 'exposed', 'MeterStatuses': 'meterstatuses', 'Status': 'status', 'Life': 'life', 'CanUpgradeTo': 'canupgradeto', 'Charm': 'charm', 'Relations': 'relations', 'Units': 'units', 'SubordinateTo': 'subordinateto'}
    def __init__(self, exposed, meterstatuses, units, life, canupgradeto, charm, relations, status, subordinateto):
        '''
        exposed : bool
        meterstatuses : typing.Mapping[str, ~MeterStatus]
        units : typing.Mapping[str, ~UnitStatus]
        life : str
        canupgradeto : str
        charm : str
        relations : typing.Sequence[str]
        status : ~DetailedStatus
        subordinateto : typing.Sequence[str]
        '''
        self.exposed = exposed
        self.meterstatuses = meterstatuses
        self.units = units
        self.life = life
        self.canupgradeto = canupgradeto
        self.charm = charm
        self.relations = relations
        self.status = status
        self.subordinateto = subordinateto


class Tools(Type):
    _toSchema = {'url': 'url', 'version': 'version', 'size': 'size', 'sha256': 'sha256'}
    _toPy = {'url': 'url', 'version': 'version', 'size': 'size', 'sha256': 'sha256'}
    def __init__(self, url, version, size, sha256):
        '''
        url : str
        version : ~Binary
        size : int
        sha256 : str
        '''
        self.url = url
        self.version = version
        self.size = size
        self.sha256 = sha256


class URL(Type):
    _toSchema = {'name': 'Name', 'schema': 'Schema', 'revision': 'Revision', 'series': 'Series', 'user': 'User', 'channel': 'Channel'}
    _toPy = {'User': 'user', 'Channel': 'channel', 'Name': 'name', 'Revision': 'revision', 'Schema': 'schema', 'Series': 'series'}
    def __init__(self, user, channel, name, revision, schema, series):
        '''
        user : str
        channel : str
        name : str
        revision : int
        schema : str
        series : str
        '''
        self.user = user
        self.channel = channel
        self.name = name
        self.revision = revision
        self.schema = schema
        self.series = series


class UnitStatus(Type):
    _toSchema = {'subordinates': 'Subordinates', 'openedports': 'OpenedPorts', 'agentstatus': 'AgentStatus', 'workloadstatus': 'WorkloadStatus', 'machine': 'Machine', 'publicaddress': 'PublicAddress', 'charm': 'Charm'}
    _toPy = {'OpenedPorts': 'openedports', 'Subordinates': 'subordinates', 'WorkloadStatus': 'workloadstatus', 'Charm': 'charm', 'PublicAddress': 'publicaddress', 'Machine': 'machine', 'AgentStatus': 'agentstatus'}
    def __init__(self, openedports, subordinates, workloadstatus, charm, publicaddress, machine, agentstatus):
        '''
        openedports : typing.Sequence[str]
        subordinates : typing.Mapping[str, ~UnitStatus]
        workloadstatus : ~DetailedStatus
        charm : str
        publicaddress : str
        machine : str
        agentstatus : ~DetailedStatus
        '''
        self.openedports = openedports
        self.subordinates = subordinates
        self.workloadstatus = workloadstatus
        self.charm = charm
        self.publicaddress = publicaddress
        self.machine = machine
        self.agentstatus = agentstatus


class Value(Type):
    _toSchema = {'mem': 'mem', 'arch': 'arch', 'container': 'container', 'spaces': 'spaces', 'root_disk': 'root-disk', 'virt_type': 'virt-type', 'cpu_power': 'cpu-power', 'tags': 'tags', 'instance_type': 'instance-type', 'cpu_cores': 'cpu-cores'}
    _toPy = {'arch': 'arch', 'root-disk': 'root_disk', 'container': 'container', 'cpu-power': 'cpu_power', 'spaces': 'spaces', 'mem': 'mem', 'virt-type': 'virt_type', 'cpu-cores': 'cpu_cores', 'instance-type': 'instance_type', 'tags': 'tags'}
    def __init__(self, arch, root_disk, container, cpu_power, virt_type, mem, spaces, cpu_cores, instance_type, tags):
        '''
        arch : str
        root_disk : int
        container : str
        cpu_power : int
        virt_type : str
        mem : int
        spaces : typing.Sequence[str]
        cpu_cores : int
        instance_type : str
        tags : typing.Sequence[str]
        '''
        self.arch = arch
        self.root_disk = root_disk
        self.container = container
        self.cpu_power = cpu_power
        self.virt_type = virt_type
        self.mem = mem
        self.spaces = spaces
        self.cpu_cores = cpu_cores
        self.instance_type = instance_type
        self.tags = tags


class InitiateModelMigrationResult(Type):
    _toSchema = {'id_': 'id', 'error': 'error', 'model_tag': 'model-tag'}
    _toPy = {'id': 'id_', 'error': 'error', 'model-tag': 'model_tag'}
    def __init__(self, id_, error, model_tag):
        '''
        id_ : str
        error : ~Error
        model_tag : str
        '''
        self.id_ = id_
        self.error = error
        self.model_tag = model_tag


class Model(Type):
    _toSchema = {'uuid': 'UUID', 'name': 'Name', 'ownertag': 'OwnerTag'}
    _toPy = {'Name': 'name', 'OwnerTag': 'ownertag', 'UUID': 'uuid'}
    def __init__(self, name, ownertag, uuid):
        '''
        name : str
        ownertag : str
        uuid : str
        '''
        self.name = name
        self.ownertag = ownertag
        self.uuid = uuid


class ModelBlockInfo(Type):
    _toSchema = {'blocks': 'blocks', 'name': 'name', 'owner_tag': 'owner-tag', 'model_uuid': 'model-uuid'}
    _toPy = {'blocks': 'blocks', 'model-uuid': 'model_uuid', 'owner-tag': 'owner_tag', 'name': 'name'}
    def __init__(self, blocks, model_uuid, owner_tag, name):
        '''
        blocks : typing.Sequence[str]
        model_uuid : str
        owner_tag : str
        name : str
        '''
        self.blocks = blocks
        self.model_uuid = model_uuid
        self.owner_tag = owner_tag
        self.name = name


class ModelMigrationSpec(Type):
    _toSchema = {'target_info': 'target-info', 'model_tag': 'model-tag'}
    _toPy = {'model-tag': 'model_tag', 'target-info': 'target_info'}
    def __init__(self, model_tag, target_info):
        '''
        model_tag : str
        target_info : ~ModelMigrationTargetInfo
        '''
        self.model_tag = model_tag
        self.target_info = target_info


class ModelMigrationTargetInfo(Type):
    _toSchema = {'controller_tag': 'controller-tag', 'addrs': 'addrs', 'password': 'password', 'auth_tag': 'auth-tag', 'ca_cert': 'ca-cert'}
    _toPy = {'auth-tag': 'auth_tag', 'controller-tag': 'controller_tag', 'addrs': 'addrs', 'ca-cert': 'ca_cert', 'password': 'password'}
    def __init__(self, auth_tag, controller_tag, addrs, ca_cert, password):
        '''
        auth_tag : str
        controller_tag : str
        addrs : typing.Sequence[str]
        ca_cert : str
        password : str
        '''
        self.auth_tag = auth_tag
        self.controller_tag = controller_tag
        self.addrs = addrs
        self.ca_cert = ca_cert
        self.password = password


class ModelStatus(Type):
    _toSchema = {'hosted_machine_count': 'hosted-machine-count', 'model_tag': 'model-tag', 'life': 'life', 'owner_tag': 'owner-tag', 'service_count': 'service-count'}
    _toPy = {'hosted-machine-count': 'hosted_machine_count', 'owner-tag': 'owner_tag', 'life': 'life', 'model-tag': 'model_tag', 'service-count': 'service_count'}
    def __init__(self, service_count, owner_tag, life, model_tag, hosted_machine_count):
        '''
        service_count : int
        owner_tag : str
        life : str
        model_tag : str
        hosted_machine_count : int
        '''
        self.service_count = service_count
        self.owner_tag = owner_tag
        self.life = life
        self.model_tag = model_tag
        self.hosted_machine_count = hosted_machine_count


class UserModel(Type):
    _toSchema = {'model': 'Model', 'lastconnection': 'LastConnection'}
    _toPy = {'Model': 'model', 'LastConnection': 'lastconnection'}
    def __init__(self, model, lastconnection):
        '''
        model : ~Model
        lastconnection : str
        '''
        self.model = model
        self.lastconnection = lastconnection


class LifeResult(Type):
    _toSchema = {'life': 'Life', 'error': 'Error'}
    _toPy = {'Life': 'life', 'Error': 'error'}
    def __init__(self, life, error):
        '''
        life : str
        error : ~Error
        '''
        self.life = life
        self.error = error


class StringsWatchResult(Type):
    _toSchema = {'changes': 'Changes', 'error': 'Error', 'stringswatcherid': 'StringsWatcherId'}
    _toPy = {'Error': 'error', 'Changes': 'changes', 'StringsWatcherId': 'stringswatcherid'}
    def __init__(self, error, changes, stringswatcherid):
        '''
        error : ~Error
        changes : typing.Sequence[str]
        stringswatcherid : str
        '''
        self.error = error
        self.changes = changes
        self.stringswatcherid = stringswatcherid


class AddSubnetParams(Type):
    _toSchema = {'subnetproviderid': 'SubnetProviderId', 'spacetag': 'SpaceTag', 'zones': 'Zones', 'subnettag': 'SubnetTag'}
    _toPy = {'SpaceTag': 'spacetag', 'SubnetProviderId': 'subnetproviderid', 'SubnetTag': 'subnettag', 'Zones': 'zones'}
    def __init__(self, spacetag, subnettag, zones, subnetproviderid):
        '''
        spacetag : str
        subnettag : str
        zones : typing.Sequence[str]
        subnetproviderid : str
        '''
        self.spacetag = spacetag
        self.subnettag = subnettag
        self.zones = zones
        self.subnetproviderid = subnetproviderid


class CreateSpaceParams(Type):
    _toSchema = {'spacetag': 'SpaceTag', 'subnettags': 'SubnetTags', 'providerid': 'ProviderId', 'public': 'Public'}
    _toPy = {'SpaceTag': 'spacetag', 'Public': 'public', 'ProviderId': 'providerid', 'SubnetTags': 'subnettags'}
    def __init__(self, spacetag, public, providerid, subnettags):
        '''
        spacetag : str
        public : bool
        providerid : str
        subnettags : typing.Sequence[str]
        '''
        self.spacetag = spacetag
        self.public = public
        self.providerid = providerid
        self.subnettags = subnettags


class ProviderSpace(Type):
    _toSchema = {'name': 'Name', 'error': 'Error', 'providerid': 'ProviderId', 'subnets': 'Subnets'}
    _toPy = {'Name': 'name', 'Error': 'error', 'ProviderId': 'providerid', 'Subnets': 'subnets'}
    def __init__(self, name, error, providerid, subnets):
        '''
        name : str
        error : ~Error
        providerid : str
        subnets : typing.Sequence[~Subnet]
        '''
        self.name = name
        self.error = error
        self.providerid = providerid
        self.subnets = subnets


class Subnet(Type):
    _toSchema = {'staticrangehighip': 'StaticRangeHighIP', 'status': 'Status', 'vlantag': 'VLANTag', 'staticrangelowip': 'StaticRangeLowIP', 'cidr': 'CIDR', 'spacetag': 'SpaceTag', 'zones': 'Zones', 'life': 'Life', 'providerid': 'ProviderId'}
    _toPy = {'SpaceTag': 'spacetag', 'ProviderId': 'providerid', 'CIDR': 'cidr', 'StaticRangeHighIP': 'staticrangehighip', 'Life': 'life', 'StaticRangeLowIP': 'staticrangelowip', 'Zones': 'zones', 'VLANTag': 'vlantag', 'Status': 'status'}
    def __init__(self, spacetag, providerid, life, staticrangehighip, cidr, staticrangelowip, zones, vlantag, status):
        '''
        spacetag : str
        providerid : str
        life : str
        staticrangehighip : typing.Sequence[int]
        cidr : str
        staticrangelowip : typing.Sequence[int]
        zones : typing.Sequence[str]
        vlantag : int
        status : str
        '''
        self.spacetag = spacetag
        self.providerid = providerid
        self.life = life
        self.staticrangehighip = staticrangehighip
        self.cidr = cidr
        self.staticrangelowip = staticrangelowip
        self.zones = zones
        self.vlantag = vlantag
        self.status = status


class BlockDevice(Type):
    _toSchema = {'busaddress': 'BusAddress', 'uuid': 'UUID', 'devicelinks': 'DeviceLinks', 'size': 'Size', 'inuse': 'InUse', 'hardwareid': 'HardwareId', 'devicename': 'DeviceName', 'label': 'Label', 'mountpoint': 'MountPoint', 'filesystemtype': 'FilesystemType'}
    _toPy = {'InUse': 'inuse', 'BusAddress': 'busaddress', 'Label': 'label', 'DeviceName': 'devicename', 'UUID': 'uuid', 'MountPoint': 'mountpoint', 'HardwareId': 'hardwareid', 'DeviceLinks': 'devicelinks', 'FilesystemType': 'filesystemtype', 'Size': 'size'}
    def __init__(self, inuse, busaddress, mountpoint, uuid, devicename, filesystemtype, hardwareid, label, devicelinks, size):
        '''
        inuse : bool
        busaddress : str
        mountpoint : str
        uuid : str
        devicename : str
        filesystemtype : str
        hardwareid : str
        label : str
        devicelinks : typing.Sequence[str]
        size : int
        '''
        self.inuse = inuse
        self.busaddress = busaddress
        self.mountpoint = mountpoint
        self.uuid = uuid
        self.devicename = devicename
        self.filesystemtype = filesystemtype
        self.hardwareid = hardwareid
        self.label = label
        self.devicelinks = devicelinks
        self.size = size


class MachineBlockDevices(Type):
    _toSchema = {'machine': 'machine', 'blockdevices': 'blockdevices'}
    _toPy = {'machine': 'machine', 'blockdevices': 'blockdevices'}
    def __init__(self, machine, blockdevices):
        '''
        machine : str
        blockdevices : typing.Sequence[~BlockDevice]
        '''
        self.machine = machine
        self.blockdevices = blockdevices


class MachineStorageId(Type):
    _toSchema = {'attachmenttag': 'attachmenttag', 'machinetag': 'machinetag'}
    _toPy = {'attachmenttag': 'attachmenttag', 'machinetag': 'machinetag'}
    def __init__(self, attachmenttag, machinetag):
        '''
        attachmenttag : str
        machinetag : str
        '''
        self.attachmenttag = attachmenttag
        self.machinetag = machinetag


class BoolResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : bool
        '''
        self.error = error
        self.result = result


class MachinePortRange(Type):
    _toSchema = {'relationtag': 'RelationTag', 'portrange': 'PortRange', 'unittag': 'UnitTag'}
    _toPy = {'RelationTag': 'relationtag', 'PortRange': 'portrange', 'UnitTag': 'unittag'}
    def __init__(self, relationtag, unittag, portrange):
        '''
        relationtag : str
        unittag : str
        portrange : ~PortRange
        '''
        self.relationtag = relationtag
        self.unittag = unittag
        self.portrange = portrange


class MachinePorts(Type):
    _toSchema = {'subnettag': 'SubnetTag', 'machinetag': 'MachineTag'}
    _toPy = {'SubnetTag': 'subnettag', 'MachineTag': 'machinetag'}
    def __init__(self, subnettag, machinetag):
        '''
        subnettag : str
        machinetag : str
        '''
        self.subnettag = subnettag
        self.machinetag = machinetag


class MachinePortsResult(Type):
    _toSchema = {'ports': 'Ports', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Ports': 'ports'}
    def __init__(self, error, ports):
        '''
        error : ~Error
        ports : typing.Sequence[~MachinePortRange]
        '''
        self.error = error
        self.ports = ports


class NotifyWatchResult(Type):
    _toSchema = {'error': 'Error', 'notifywatcherid': 'NotifyWatcherId'}
    _toPy = {'Error': 'error', 'NotifyWatcherId': 'notifywatcherid'}
    def __init__(self, error, notifywatcherid):
        '''
        error : ~Error
        notifywatcherid : str
        '''
        self.error = error
        self.notifywatcherid = notifywatcherid


class PortRange(Type):
    _toSchema = {'toport': 'ToPort', 'protocol': 'Protocol', 'fromport': 'FromPort'}
    _toPy = {'FromPort': 'fromport', 'ToPort': 'toport', 'Protocol': 'protocol'}
    def __init__(self, fromport, toport, protocol):
        '''
        fromport : int
        toport : int
        protocol : str
        '''
        self.fromport = fromport
        self.toport = toport
        self.protocol = protocol


class StringResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : str
        '''
        self.error = error
        self.result = result


class StringsResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : typing.Sequence[str]
        '''
        self.error = error
        self.result = result


class ControllersChangeResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~ControllersChanges
        '''
        self.error = error
        self.result = result


class ControllersChanges(Type):
    _toSchema = {'added': 'added', 'removed': 'removed', 'promoted': 'promoted', 'maintained': 'maintained', 'demoted': 'demoted', 'converted': 'converted'}
    _toPy = {'added': 'added', 'removed': 'removed', 'promoted': 'promoted', 'maintained': 'maintained', 'demoted': 'demoted', 'converted': 'converted'}
    def __init__(self, added, removed, promoted, maintained, demoted, converted):
        '''
        added : typing.Sequence[str]
        removed : typing.Sequence[str]
        promoted : typing.Sequence[str]
        maintained : typing.Sequence[str]
        demoted : typing.Sequence[str]
        converted : typing.Sequence[str]
        '''
        self.added = added
        self.removed = removed
        self.promoted = promoted
        self.maintained = maintained
        self.demoted = demoted
        self.converted = converted


class ControllersSpec(Type):
    _toSchema = {'placement': 'placement', 'constraints': 'constraints', 'series': 'series', 'num_controllers': 'num-controllers', 'modeltag': 'ModelTag'}
    _toPy = {'ModelTag': 'modeltag', 'num-controllers': 'num_controllers', 'constraints': 'constraints', 'series': 'series', 'placement': 'placement'}
    def __init__(self, modeltag, num_controllers, constraints, series, placement):
        '''
        modeltag : str
        num_controllers : int
        constraints : ~Value
        series : str
        placement : typing.Sequence[str]
        '''
        self.modeltag = modeltag
        self.num_controllers = num_controllers
        self.constraints = constraints
        self.series = series
        self.placement = placement


class HAMember(Type):
    _toSchema = {'series': 'Series', 'publicaddress': 'PublicAddress', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'PublicAddress': 'publicaddress', 'Series': 'series'}
    def __init__(self, tag, series, publicaddress):
        '''
        tag : str
        series : str
        publicaddress : ~Address
        '''
        self.tag = tag
        self.series = series
        self.publicaddress = publicaddress


class Member(Type):
    _toSchema = {'address': 'Address', 'id_': 'Id', 'priority': 'Priority', 'buildindexes': 'BuildIndexes', 'slavedelay': 'SlaveDelay', 'arbiter': 'Arbiter', 'hidden': 'Hidden', 'votes': 'Votes', 'tags': 'Tags'}
    _toPy = {'Id': 'id_', 'Hidden': 'hidden', 'Votes': 'votes', 'SlaveDelay': 'slavedelay', 'Tags': 'tags', 'Address': 'address', 'Arbiter': 'arbiter', 'Priority': 'priority', 'BuildIndexes': 'buildindexes'}
    def __init__(self, id_, hidden, votes, slavedelay, tags, priority, arbiter, buildindexes, address):
        '''
        id_ : int
        hidden : bool
        votes : int
        slavedelay : int
        tags : typing.Mapping[str, str]
        priority : float
        arbiter : bool
        buildindexes : bool
        address : str
        '''
        self.id_ = id_
        self.hidden = hidden
        self.votes = votes
        self.slavedelay = slavedelay
        self.tags = tags
        self.priority = priority
        self.arbiter = arbiter
        self.buildindexes = buildindexes
        self.address = address


class Version(Type):
    _toSchema = {'major': 'Major', 'minor': 'Minor', 'storageengine': 'StorageEngine', 'patch': 'Patch'}
    _toPy = {'Minor': 'minor', 'Patch': 'patch', 'Major': 'major', 'StorageEngine': 'storageengine'}
    def __init__(self, minor, patch, major, storageengine):
        '''
        minor : int
        patch : str
        major : int
        storageengine : str
        '''
        self.minor = minor
        self.patch = patch
        self.major = major
        self.storageengine = storageengine


class SSHHostKeys(Type):
    _toSchema = {'public_keys': 'public-keys', 'tag': 'tag'}
    _toPy = {'public-keys': 'public_keys', 'tag': 'tag'}
    def __init__(self, tag, public_keys):
        '''
        tag : str
        public_keys : typing.Sequence[str]
        '''
        self.tag = tag
        self.public_keys = public_keys


class ImageMetadata(Type):
    _toSchema = {'kind': 'kind', 'url': 'url', 'arch': 'arch', 'series': 'series', 'created': 'created'}
    _toPy = {'kind': 'kind', 'url': 'url', 'arch': 'arch', 'series': 'series', 'created': 'created'}
    def __init__(self, kind, url, arch, series, created):
        '''
        kind : str
        url : str
        arch : str
        series : str
        created : str
        '''
        self.kind = kind
        self.url = url
        self.arch = arch
        self.series = series
        self.created = created


class ImageSpec(Type):
    _toSchema = {'kind': 'kind', 'arch': 'arch', 'series': 'series'}
    _toPy = {'kind': 'kind', 'arch': 'arch', 'series': 'series'}
    def __init__(self, kind, arch, series):
        '''
        kind : str
        arch : str
        series : str
        '''
        self.kind = kind
        self.arch = arch
        self.series = series


class CloudImageMetadata(Type):
    _toSchema = {'source': 'source', 'arch': 'arch', 'image_id': 'image_id', 'root_storage_size': 'root_storage_size', 'priority': 'priority', 'virt_type': 'virt_type', 'version': 'version', 'series': 'series', 'stream': 'stream', 'root_storage_type': 'root_storage_type', 'region': 'region'}
    _toPy = {'source': 'source', 'arch': 'arch', 'image_id': 'image_id', 'root_storage_size': 'root_storage_size', 'priority': 'priority', 'virt_type': 'virt_type', 'version': 'version', 'series': 'series', 'stream': 'stream', 'root_storage_type': 'root_storage_type', 'region': 'region'}
    def __init__(self, root_storage_type, source, arch, image_id, priority, virt_type, version, series, stream, region, root_storage_size):
        '''
        root_storage_type : str
        source : str
        arch : str
        image_id : str
        priority : int
        virt_type : str
        version : str
        series : str
        stream : str
        region : str
        root_storage_size : int
        '''
        self.root_storage_type = root_storage_type
        self.source = source
        self.arch = arch
        self.image_id = image_id
        self.priority = priority
        self.virt_type = virt_type
        self.version = version
        self.series = series
        self.stream = stream
        self.region = region
        self.root_storage_size = root_storage_size


class CloudImageMetadataList(Type):
    _toSchema = {'metadata': 'metadata'}
    _toPy = {'metadata': 'metadata'}
    def __init__(self, metadata):
        '''
        metadata : typing.Sequence[~CloudImageMetadata]
        '''
        self.metadata = metadata


class EntityStatusArgs(Type):
    _toSchema = {'info': 'Info', 'status': 'Status', 'data': 'Data', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Info': 'info', 'Data': 'data', 'Status': 'status'}
    def __init__(self, tag, info, data, status):
        '''
        tag : str
        info : str
        data : typing.Mapping[str, typing.Any]
        status : str
        '''
        self.tag = tag
        self.info = info
        self.data = data
        self.status = status


class MachineAddresses(Type):
    _toSchema = {'addresses': 'Addresses', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Addresses': 'addresses'}
    def __init__(self, tag, addresses):
        '''
        tag : str
        addresses : typing.Sequence[~Address]
        '''
        self.tag = tag
        self.addresses = addresses


class MachineAddressesResult(Type):
    _toSchema = {'addresses': 'Addresses', 'error': 'Error'}
    _toPy = {'Addresses': 'addresses', 'Error': 'error'}
    def __init__(self, addresses, error):
        '''
        addresses : typing.Sequence[~Address]
        error : ~Error
        '''
        self.addresses = addresses
        self.error = error


class StatusResult(Type):
    _toSchema = {'info': 'Info', 'id_': 'Id', 'status': 'Status', 'since': 'Since', 'life': 'Life', 'data': 'Data', 'error': 'Error'}
    _toPy = {'Id': 'id_', 'Data': 'data', 'Life': 'life', 'Error': 'error', 'Info': 'info', 'Status': 'status', 'Since': 'since'}
    def __init__(self, info, data, life, error, id_, status, since):
        '''
        info : str
        data : typing.Mapping[str, typing.Any]
        life : str
        error : ~Error
        id_ : str
        status : str
        since : str
        '''
        self.info = info
        self.data = data
        self.life = life
        self.error = error
        self.id_ = id_
        self.status = status
        self.since = since


class Entities(Type):
    _toSchema = {'entities': 'Entities'}
    _toPy = {'Entities': 'entities'}
    def __init__(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        '''
        self.entities = entities


class ClaimLeadershipParams(Type):
    _toSchema = {'durationseconds': 'DurationSeconds', 'unittag': 'UnitTag', 'servicetag': 'ServiceTag'}
    _toPy = {'DurationSeconds': 'durationseconds', 'ServiceTag': 'servicetag', 'UnitTag': 'unittag'}
    def __init__(self, durationseconds, servicetag, unittag):
        '''
        durationseconds : float
        servicetag : str
        unittag : str
        '''
        self.durationseconds = durationseconds
        self.servicetag = servicetag
        self.unittag = unittag


class ActionExecutionResult(Type):
    _toSchema = {'actiontag': 'actiontag', 'results': 'results', 'status': 'status', 'message': 'message'}
    _toPy = {'actiontag': 'actiontag', 'results': 'results', 'status': 'status', 'message': 'message'}
    def __init__(self, status, results, actiontag, message):
        '''
        status : str
        results : typing.Mapping[str, typing.Any]
        actiontag : str
        message : str
        '''
        self.status = status
        self.results = results
        self.actiontag = actiontag
        self.message = message


class JobsResult(Type):
    _toSchema = {'error': 'Error', 'jobs': 'Jobs'}
    _toPy = {'Error': 'error', 'Jobs': 'jobs'}
    def __init__(self, error, jobs):
        '''
        error : ~Error
        jobs : typing.Sequence[str]
        '''
        self.error = error
        self.jobs = jobs


class NetworkConfig(Type):
    _toSchema = {'disabled': 'Disabled', 'mtu': 'MTU', 'configtype': 'ConfigType', 'provideraddressid': 'ProviderAddressId', 'interfacename': 'InterfaceName', 'parentinterfacename': 'ParentInterfaceName', 'deviceindex': 'DeviceIndex', 'noautostart': 'NoAutoStart', 'providerid': 'ProviderId', 'address': 'Address', 'providersubnetid': 'ProviderSubnetId', 'providervlanid': 'ProviderVLANId', 'macaddress': 'MACAddress', 'providerspaceid': 'ProviderSpaceId', 'vlantag': 'VLANTag', 'interfacetype': 'InterfaceType', 'cidr': 'CIDR', 'dnsservers': 'DNSServers', 'gatewayaddress': 'GatewayAddress', 'dnssearchdomains': 'DNSSearchDomains'}
    _toPy = {'DeviceIndex': 'deviceindex', 'MACAddress': 'macaddress', 'ProviderAddressId': 'provideraddressid', 'MTU': 'mtu', 'DNSSearchDomains': 'dnssearchdomains', 'CIDR': 'cidr', 'ProviderVLANId': 'providervlanid', 'DNSServers': 'dnsservers', 'NoAutoStart': 'noautostart', 'InterfaceType': 'interfacetype', 'Address': 'address', 'ConfigType': 'configtype', 'GatewayAddress': 'gatewayaddress', 'ProviderSpaceId': 'providerspaceid', 'ProviderSubnetId': 'providersubnetid', 'Disabled': 'disabled', 'ProviderId': 'providerid', 'InterfaceName': 'interfacename', 'ParentInterfaceName': 'parentinterfacename', 'VLANTag': 'vlantag'}
    def __init__(self, deviceindex, provideraddressid, mtu, vlantag, dnssearchdomains, cidr, providervlanid, dnsservers, noautostart, interfacetype, address, parentinterfacename, configtype, gatewayaddress, providerspaceid, providersubnetid, disabled, interfacename, macaddress, providerid):
        '''
        deviceindex : int
        provideraddressid : str
        mtu : int
        vlantag : int
        dnssearchdomains : typing.Sequence[str]
        cidr : str
        providervlanid : str
        dnsservers : typing.Sequence[str]
        noautostart : bool
        interfacetype : str
        address : str
        parentinterfacename : str
        configtype : str
        gatewayaddress : str
        providerspaceid : str
        providersubnetid : str
        disabled : bool
        interfacename : str
        macaddress : str
        providerid : str
        '''
        self.deviceindex = deviceindex
        self.provideraddressid = provideraddressid
        self.mtu = mtu
        self.vlantag = vlantag
        self.dnssearchdomains = dnssearchdomains
        self.cidr = cidr
        self.providervlanid = providervlanid
        self.dnsservers = dnsservers
        self.noautostart = noautostart
        self.interfacetype = interfacetype
        self.address = address
        self.parentinterfacename = parentinterfacename
        self.configtype = configtype
        self.gatewayaddress = gatewayaddress
        self.providerspaceid = providerspaceid
        self.providersubnetid = providersubnetid
        self.disabled = disabled
        self.interfacename = interfacename
        self.macaddress = macaddress
        self.providerid = providerid


class MeterStatusResult(Type):
    _toSchema = {'info': 'Info', 'code': 'Code', 'error': 'Error'}
    _toPy = {'Info': 'info', 'Error': 'error', 'Code': 'code'}
    def __init__(self, info, error, code):
        '''
        info : str
        error : ~Error
        code : str
        '''
        self.info = info
        self.error = error
        self.code = code


class Metric(Type):
    _toSchema = {'key': 'Key', 'value': 'Value', 'time': 'Time'}
    _toPy = {'Value': 'value', 'Key': 'key', 'Time': 'time'}
    def __init__(self, value, key, time):
        '''
        value : str
        key : str
        time : str
        '''
        self.value = value
        self.key = key
        self.time = time


class MetricBatch(Type):
    _toSchema = {'metrics': 'Metrics', 'uuid': 'UUID', 'charmurl': 'CharmURL', 'created': 'Created'}
    _toPy = {'Created': 'created', 'CharmURL': 'charmurl', 'Metrics': 'metrics', 'UUID': 'uuid'}
    def __init__(self, created, charmurl, metrics, uuid):
        '''
        created : str
        charmurl : str
        metrics : typing.Sequence[~Metric]
        uuid : str
        '''
        self.created = created
        self.charmurl = charmurl
        self.metrics = metrics
        self.uuid = uuid


class MetricBatchParam(Type):
    _toSchema = {'batch': 'Batch', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Batch': 'batch'}
    def __init__(self, tag, batch):
        '''
        tag : str
        batch : ~MetricBatch
        '''
        self.tag = tag
        self.batch = batch


class EntityMetrics(Type):
    _toSchema = {'metrics': 'metrics', 'error': 'error'}
    _toPy = {'metrics': 'metrics', 'error': 'error'}
    def __init__(self, metrics, error):
        '''
        metrics : typing.Sequence[~MetricResult]
        error : ~Error
        '''
        self.metrics = metrics
        self.error = error


class MeterStatusParam(Type):
    _toSchema = {'info': 'info', 'code': 'code', 'tag': 'tag'}
    _toPy = {'info': 'info', 'code': 'code', 'tag': 'tag'}
    def __init__(self, info, code, tag):
        '''
        info : str
        code : str
        tag : str
        '''
        self.info = info
        self.code = code
        self.tag = tag


class MetricResult(Type):
    _toSchema = {'key': 'key', 'value': 'value', 'time': 'time'}
    _toPy = {'key': 'key', 'value': 'value', 'time': 'time'}
    def __init__(self, key, value, time):
        '''
        key : str
        value : str
        time : str
        '''
        self.key = key
        self.value = value
        self.time = time


class PhaseResult(Type):
    _toSchema = {'phase': 'phase', 'error': 'Error'}
    _toPy = {'Error': 'error', 'phase': 'phase'}
    def __init__(self, error, phase):
        '''
        error : ~Error
        phase : str
        '''
        self.error = error
        self.phase = phase


class ModelInfo(Type):
    _toSchema = {'uuid': 'UUID', 'name': 'Name', 'ownertag': 'OwnerTag', 'serveruuid': 'ServerUUID', 'providertype': 'ProviderType', 'defaultseries': 'DefaultSeries', 'users': 'Users', 'life': 'Life', 'status': 'Status'}
    _toPy = {'DefaultSeries': 'defaultseries', 'ProviderType': 'providertype', 'Status': 'status', 'UUID': 'uuid', 'Name': 'name', 'ServerUUID': 'serveruuid', 'Life': 'life', 'OwnerTag': 'ownertag', 'Users': 'users'}
    def __init__(self, defaultseries, providertype, serveruuid, users, uuid, name, life, ownertag, status):
        '''
        defaultseries : str
        providertype : str
        serveruuid : str
        users : typing.Sequence[~ModelUserInfo]
        uuid : str
        name : str
        life : str
        ownertag : str
        status : ~EntityStatus
        '''
        self.defaultseries = defaultseries
        self.providertype = providertype
        self.serveruuid = serveruuid
        self.users = users
        self.uuid = uuid
        self.name = name
        self.life = life
        self.ownertag = ownertag
        self.status = status


class ModelInfoResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~ModelInfo
        '''
        self.error = error
        self.result = result


class ModifyModelAccess(Type):
    _toSchema = {'action': 'action', 'user_tag': 'user-tag', 'access': 'access', 'model_tag': 'model-tag'}
    _toPy = {'action': 'action', 'model-tag': 'model_tag', 'user-tag': 'user_tag', 'access': 'access'}
    def __init__(self, action, user_tag, access, model_tag):
        '''
        action : str
        user_tag : str
        access : str
        model_tag : str
        '''
        self.action = action
        self.user_tag = user_tag
        self.access = access
        self.model_tag = model_tag


class ConstraintsResult(Type):
    _toSchema = {'constraints': 'Constraints', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Constraints': 'constraints'}
    def __init__(self, error, constraints):
        '''
        error : ~Error
        constraints : ~Value
        '''
        self.error = error
        self.constraints = constraints


class DistributionGroupResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : typing.Sequence[str]
        '''
        self.error = error
        self.result = result


class InstanceInfo(Type):
    _toSchema = {'nonce': 'Nonce', 'tag': 'Tag', 'instanceid': 'InstanceId', 'characteristics': 'Characteristics', 'volumes': 'Volumes', 'networkconfig': 'NetworkConfig', 'volumeattachments': 'VolumeAttachments'}
    _toPy = {'Characteristics': 'characteristics', 'InstanceId': 'instanceid', 'Tag': 'tag', 'Volumes': 'volumes', 'NetworkConfig': 'networkconfig', 'Nonce': 'nonce', 'VolumeAttachments': 'volumeattachments'}
    def __init__(self, volumes, characteristics, nonce, tag, instanceid, networkconfig, volumeattachments):
        '''
        volumes : typing.Sequence[~Volume]
        characteristics : ~HardwareCharacteristics
        nonce : str
        tag : str
        instanceid : str
        networkconfig : typing.Sequence[~NetworkConfig]
        volumeattachments : typing.Mapping[str, ~VolumeAttachmentInfo]
        '''
        self.volumes = volumes
        self.characteristics = characteristics
        self.nonce = nonce
        self.tag = tag
        self.instanceid = instanceid
        self.networkconfig = networkconfig
        self.volumeattachments = volumeattachments


class MachineContainers(Type):
    _toSchema = {'containertypes': 'ContainerTypes', 'machinetag': 'MachineTag'}
    _toPy = {'ContainerTypes': 'containertypes', 'MachineTag': 'machinetag'}
    def __init__(self, containertypes, machinetag):
        '''
        containertypes : typing.Sequence[str]
        machinetag : str
        '''
        self.containertypes = containertypes
        self.machinetag = machinetag


class MachineNetworkConfigResult(Type):
    _toSchema = {'info': 'Info', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Info': 'info'}
    def __init__(self, error, info):
        '''
        error : ~Error
        info : typing.Sequence[~NetworkConfig]
        '''
        self.error = error
        self.info = info


class ProvisioningInfo(Type):
    _toSchema = {'endpointbindings': 'EndpointBindings', 'constraints': 'Constraints', 'imagemetadata': 'ImageMetadata', 'jobs': 'Jobs', 'subnetstozones': 'SubnetsToZones', 'series': 'Series', 'volumes': 'Volumes', 'placement': 'Placement', 'tags': 'Tags'}
    _toPy = {'Series': 'series', 'Constraints': 'constraints', 'ImageMetadata': 'imagemetadata', 'Volumes': 'volumes', 'Tags': 'tags', 'Jobs': 'jobs', 'SubnetsToZones': 'subnetstozones', 'EndpointBindings': 'endpointbindings', 'Placement': 'placement'}
    def __init__(self, series, constraints, subnetstozones, tags, volumes, endpointbindings, placement, jobs, imagemetadata):
        '''
        series : str
        constraints : ~Value
        subnetstozones : typing.Sequence[str]
        tags : typing.Mapping[str, str]
        volumes : typing.Sequence[~VolumeParams]
        endpointbindings : typing.Mapping[str, str]
        placement : str
        jobs : typing.Sequence[str]
        imagemetadata : typing.Sequence[~CloudImageMetadata]
        '''
        self.series = series
        self.constraints = constraints
        self.subnetstozones = subnetstozones
        self.tags = tags
        self.volumes = volumes
        self.endpointbindings = endpointbindings
        self.placement = placement
        self.jobs = jobs
        self.imagemetadata = imagemetadata


class ProvisioningInfoResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~ProvisioningInfo
        '''
        self.error = error
        self.result = result


class Settings(Type):
    _toSchema = {'http': 'Http', 'noproxy': 'NoProxy', 'ftp': 'Ftp', 'https': 'Https'}
    _toPy = {'Https': 'https', 'Http': 'http', 'NoProxy': 'noproxy', 'Ftp': 'ftp'}
    def __init__(self, https, ftp, noproxy, http):
        '''
        https : str
        ftp : str
        noproxy : str
        http : str
        '''
        self.https = https
        self.ftp = ftp
        self.noproxy = noproxy
        self.http = http


class ToolsResult(Type):
    _toSchema = {'disablesslhostnameverification': 'DisableSSLHostnameVerification', 'toolslist': 'ToolsList', 'error': 'Error'}
    _toPy = {'DisableSSLHostnameVerification': 'disablesslhostnameverification', 'Error': 'error', 'ToolsList': 'toolslist'}
    def __init__(self, disablesslhostnameverification, error, toolslist):
        '''
        disablesslhostnameverification : bool
        error : ~Error
        toolslist : typing.Sequence[~Tools]
        '''
        self.disablesslhostnameverification = disablesslhostnameverification
        self.error = error
        self.toolslist = toolslist


class UpdateBehavior(Type):
    _toSchema = {'enableosupgrade': 'EnableOSUpgrade', 'enableosrefreshupdate': 'EnableOSRefreshUpdate'}
    _toPy = {'EnableOSUpgrade': 'enableosupgrade', 'EnableOSRefreshUpdate': 'enableosrefreshupdate'}
    def __init__(self, enableosupgrade, enableosrefreshupdate):
        '''
        enableosupgrade : bool
        enableosrefreshupdate : bool
        '''
        self.enableosupgrade = enableosupgrade
        self.enableosrefreshupdate = enableosrefreshupdate


class Volume(Type):
    _toSchema = {'info': 'info', 'volumetag': 'volumetag'}
    _toPy = {'info': 'info', 'volumetag': 'volumetag'}
    def __init__(self, info, volumetag):
        '''
        info : ~VolumeInfo
        volumetag : str
        '''
        self.info = info
        self.volumetag = volumetag


class VolumeAttachmentInfo(Type):
    _toSchema = {'busaddress': 'busaddress', 'devicelink': 'devicelink', 'read_only': 'read-only', 'devicename': 'devicename'}
    _toPy = {'busaddress': 'busaddress', 'devicelink': 'devicelink', 'read-only': 'read_only', 'devicename': 'devicename'}
    def __init__(self, busaddress, devicelink, read_only, devicename):
        '''
        busaddress : str
        devicelink : str
        read_only : bool
        devicename : str
        '''
        self.busaddress = busaddress
        self.devicelink = devicelink
        self.read_only = read_only
        self.devicename = devicename


class VolumeAttachmentParams(Type):
    _toSchema = {'provider': 'provider', 'instanceid': 'instanceid', 'read_only': 'read-only', 'volumetag': 'volumetag', 'machinetag': 'machinetag', 'volumeid': 'volumeid'}
    _toPy = {'provider': 'provider', 'instanceid': 'instanceid', 'read-only': 'read_only', 'volumetag': 'volumetag', 'machinetag': 'machinetag', 'volumeid': 'volumeid'}
    def __init__(self, volumetag, provider, instanceid, read_only, volumeid, machinetag):
        '''
        volumetag : str
        provider : str
        instanceid : str
        read_only : bool
        volumeid : str
        machinetag : str
        '''
        self.volumetag = volumetag
        self.provider = provider
        self.instanceid = instanceid
        self.read_only = read_only
        self.volumeid = volumeid
        self.machinetag = machinetag


class VolumeInfo(Type):
    _toSchema = {'hardwareid': 'hardwareid', 'persistent': 'persistent', 'size': 'size', 'volumeid': 'volumeid'}
    _toPy = {'hardwareid': 'hardwareid', 'persistent': 'persistent', 'size': 'size', 'volumeid': 'volumeid'}
    def __init__(self, hardwareid, persistent, size, volumeid):
        '''
        hardwareid : str
        persistent : bool
        size : int
        volumeid : str
        '''
        self.hardwareid = hardwareid
        self.persistent = persistent
        self.size = size
        self.volumeid = volumeid


class VolumeParams(Type):
    _toSchema = {'provider': 'provider', 'size': 'size', 'volumetag': 'volumetag', 'attachment': 'attachment', 'attributes': 'attributes', 'tags': 'tags'}
    _toPy = {'provider': 'provider', 'size': 'size', 'volumetag': 'volumetag', 'attachment': 'attachment', 'attributes': 'attributes', 'tags': 'tags'}
    def __init__(self, provider, size, volumetag, attachment, attributes, tags):
        '''
        provider : str
        size : int
        volumetag : str
        attachment : ~VolumeAttachmentParams
        attributes : typing.Mapping[str, typing.Any]
        tags : typing.Mapping[str, str]
        '''
        self.provider = provider
        self.size = size
        self.volumetag = volumetag
        self.attachment = attachment
        self.attributes = attributes
        self.tags = tags


class WatchContainer(Type):
    _toSchema = {'containertype': 'ContainerType', 'machinetag': 'MachineTag'}
    _toPy = {'ContainerType': 'containertype', 'MachineTag': 'machinetag'}
    def __init__(self, machinetag, containertype):
        '''
        machinetag : str
        containertype : str
        '''
        self.machinetag = machinetag
        self.containertype = containertype


class ProxyConfig(Type):
    _toSchema = {'http': 'HTTP', 'noproxy': 'NoProxy', 'ftp': 'FTP', 'https': 'HTTPS'}
    _toPy = {'HTTP': 'http', 'FTP': 'ftp', 'NoProxy': 'noproxy', 'HTTPS': 'https'}
    def __init__(self, http, ftp, noproxy, https):
        '''
        http : str
        ftp : str
        noproxy : str
        https : str
        '''
        self.http = http
        self.ftp = ftp
        self.noproxy = noproxy
        self.https = https


class ProxyConfigResult(Type):
    _toSchema = {'proxysettings': 'ProxySettings', 'aptproxysettings': 'APTProxySettings', 'error': 'Error'}
    _toPy = {'APTProxySettings': 'aptproxysettings', 'Error': 'error', 'ProxySettings': 'proxysettings'}
    def __init__(self, aptproxysettings, error, proxysettings):
        '''
        aptproxysettings : ~ProxyConfig
        error : ~Error
        proxysettings : ~ProxyConfig
        '''
        self.aptproxysettings = aptproxysettings
        self.error = error
        self.proxysettings = proxysettings


class RebootActionResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : str
        '''
        self.error = error
        self.result = result


class RelationUnitsChange(Type):
    _toSchema = {'departed': 'Departed', 'changed': 'Changed'}
    _toPy = {'Departed': 'departed', 'Changed': 'changed'}
    def __init__(self, departed, changed):
        '''
        departed : typing.Sequence[str]
        changed : typing.Mapping[str, ~UnitSettings]
        '''
        self.departed = departed
        self.changed = changed


class UnitSettings(Type):
    _toSchema = {'version': 'Version'}
    _toPy = {'Version': 'version'}
    def __init__(self, version):
        '''
        version : int
        '''
        self.version = version


class RetryStrategy(Type):
    _toSchema = {'shouldretry': 'ShouldRetry', 'minretrytime': 'MinRetryTime', 'jitterretrytime': 'JitterRetryTime', 'retrytimefactor': 'RetryTimeFactor', 'maxretrytime': 'MaxRetryTime'}
    _toPy = {'JitterRetryTime': 'jitterretrytime', 'MinRetryTime': 'minretrytime', 'ShouldRetry': 'shouldretry', 'RetryTimeFactor': 'retrytimefactor', 'MaxRetryTime': 'maxretrytime'}
    def __init__(self, jitterretrytime, minretrytime, shouldretry, retrytimefactor, maxretrytime):
        '''
        jitterretrytime : bool
        minretrytime : int
        shouldretry : bool
        retrytimefactor : int
        maxretrytime : int
        '''
        self.jitterretrytime = jitterretrytime
        self.minretrytime = minretrytime
        self.shouldretry = shouldretry
        self.retrytimefactor = retrytimefactor
        self.maxretrytime = maxretrytime


class RetryStrategyResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~RetryStrategy
        '''
        self.error = error
        self.result = result


class SSHAddressResult(Type):
    _toSchema = {'error': 'error', 'address': 'address'}
    _toPy = {'error': 'error', 'address': 'address'}
    def __init__(self, error, address):
        '''
        error : ~Error
        address : str
        '''
        self.error = error
        self.address = address


class SSHPublicKeysResult(Type):
    _toSchema = {'error': 'error', 'public_keys': 'public-keys'}
    _toPy = {'error': 'error', 'public-keys': 'public_keys'}
    def __init__(self, error, public_keys):
        '''
        error : ~Error
        public_keys : typing.Sequence[str]
        '''
        self.error = error
        self.public_keys = public_keys


class Relation(Type):
    _toSchema = {'name': 'Name', 'optional': 'Optional', 'role': 'Role', 'interface': 'Interface', 'scope': 'Scope', 'limit': 'Limit'}
    _toPy = {'Interface': 'interface', 'Limit': 'limit', 'Role': 'role', 'Name': 'name', 'Optional': 'optional', 'Scope': 'scope'}
    def __init__(self, interface, limit, role, name, scope, optional):
        '''
        interface : str
        limit : int
        role : str
        name : str
        scope : str
        optional : bool
        '''
        self.interface = interface
        self.limit = limit
        self.role = role
        self.name = name
        self.scope = scope
        self.optional = optional


class ServiceDeploy(Type):
    _toSchema = {'endpointbindings': 'EndpointBindings', 'placement': 'Placement', 'series': 'Series', 'resources': 'Resources', 'config': 'Config', 'constraints': 'Constraints', 'channel': 'Channel', 'configyaml': 'ConfigYAML', 'charmurl': 'CharmUrl', 'storage': 'Storage', 'servicename': 'ServiceName', 'numunits': 'NumUnits'}
    _toPy = {'CharmUrl': 'charmurl', 'Resources': 'resources', 'Channel': 'channel', 'Constraints': 'constraints', 'Placement': 'placement', 'EndpointBindings': 'endpointbindings', 'ConfigYAML': 'configyaml', 'ServiceName': 'servicename', 'Series': 'series', 'Config': 'config', 'NumUnits': 'numunits', 'Storage': 'storage'}
    def __init__(self, charmurl, resources, channel, constraints, placement, endpointbindings, configyaml, servicename, series, config, numunits, storage):
        '''
        charmurl : str
        resources : typing.Mapping[str, str]
        channel : str
        constraints : ~Value
        placement : typing.Sequence[~Placement]
        endpointbindings : typing.Mapping[str, str]
        configyaml : str
        servicename : str
        series : str
        config : typing.Mapping[str, str]
        numunits : int
        storage : typing.Mapping[str, ~Constraints]
        '''
        self.charmurl = charmurl
        self.resources = resources
        self.channel = channel
        self.constraints = constraints
        self.placement = placement
        self.endpointbindings = endpointbindings
        self.configyaml = configyaml
        self.servicename = servicename
        self.series = series
        self.config = config
        self.numunits = numunits
        self.storage = storage


class ServiceMetricCredential(Type):
    _toSchema = {'servicename': 'ServiceName', 'metriccredentials': 'MetricCredentials'}
    _toPy = {'MetricCredentials': 'metriccredentials', 'ServiceName': 'servicename'}
    def __init__(self, metriccredentials, servicename):
        '''
        metriccredentials : typing.Sequence[int]
        servicename : str
        '''
        self.metriccredentials = metriccredentials
        self.servicename = servicename


class SingularClaim(Type):
    _toSchema = {'duration': 'Duration', 'modeltag': 'ModelTag', 'controllertag': 'ControllerTag'}
    _toPy = {'ModelTag': 'modeltag', 'ControllerTag': 'controllertag', 'Duration': 'duration'}
    def __init__(self, modeltag, controllertag, duration):
        '''
        modeltag : str
        controllertag : str
        duration : int
        '''
        self.modeltag = modeltag
        self.controllertag = controllertag
        self.duration = duration


class Space(Type):
    _toSchema = {'name': 'Name', 'error': 'Error', 'subnets': 'Subnets'}
    _toPy = {'Name': 'name', 'Error': 'error', 'Subnets': 'subnets'}
    def __init__(self, name, error, subnets):
        '''
        name : str
        error : ~Error
        subnets : typing.Sequence[~Subnet]
        '''
        self.name = name
        self.error = error
        self.subnets = subnets


class FilesystemAttachmentInfo(Type):
    _toSchema = {'read_only': 'read-only', 'mountpoint': 'mountpoint'}
    _toPy = {'read-only': 'read_only', 'mountpoint': 'mountpoint'}
    def __init__(self, read_only, mountpoint):
        '''
        read_only : bool
        mountpoint : str
        '''
        self.read_only = read_only
        self.mountpoint = mountpoint


class FilesystemDetails(Type):
    _toSchema = {'info': 'info', 'status': 'status', 'machineattachments': 'machineattachments', 'storage': 'storage', 'volumetag': 'volumetag', 'filesystemtag': 'filesystemtag'}
    _toPy = {'info': 'info', 'status': 'status', 'machineattachments': 'machineattachments', 'storage': 'storage', 'volumetag': 'volumetag', 'filesystemtag': 'filesystemtag'}
    def __init__(self, info, status, filesystemtag, storage, volumetag, machineattachments):
        '''
        info : ~FilesystemInfo
        status : ~EntityStatus
        filesystemtag : str
        storage : ~StorageDetails
        volumetag : str
        machineattachments : typing.Mapping[str, ~FilesystemAttachmentInfo]
        '''
        self.info = info
        self.status = status
        self.filesystemtag = filesystemtag
        self.storage = storage
        self.volumetag = volumetag
        self.machineattachments = machineattachments


class FilesystemDetailsListResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : typing.Sequence[~FilesystemDetails]
        '''
        self.error = error
        self.result = result


class FilesystemFilter(Type):
    _toSchema = {'machines': 'machines'}
    _toPy = {'machines': 'machines'}
    def __init__(self, machines):
        '''
        machines : typing.Sequence[str]
        '''
        self.machines = machines


class FilesystemInfo(Type):
    _toSchema = {'filesystemid': 'filesystemid', 'size': 'size'}
    _toPy = {'filesystemid': 'filesystemid', 'size': 'size'}
    def __init__(self, filesystemid, size):
        '''
        filesystemid : str
        size : int
        '''
        self.filesystemid = filesystemid
        self.size = size


class StorageAddParams(Type):
    _toSchema = {'storage': 'storage', 'unit': 'unit', 'storagename': 'StorageName'}
    _toPy = {'StorageName': 'storagename', 'unit': 'unit', 'storage': 'storage'}
    def __init__(self, storagename, unit, storage):
        '''
        storagename : str
        unit : str
        storage : ~StorageConstraints
        '''
        self.storagename = storagename
        self.unit = unit
        self.storage = storage


class StorageAttachmentDetails(Type):
    _toSchema = {'unittag': 'unittag', 'location': 'location', 'storagetag': 'storagetag', 'machinetag': 'machinetag'}
    _toPy = {'unittag': 'unittag', 'location': 'location', 'storagetag': 'storagetag', 'machinetag': 'machinetag'}
    def __init__(self, unittag, location, storagetag, machinetag):
        '''
        unittag : str
        location : str
        storagetag : str
        machinetag : str
        '''
        self.unittag = unittag
        self.location = location
        self.storagetag = storagetag
        self.machinetag = machinetag


class StorageConstraints(Type):
    _toSchema = {'size': 'Size', 'pool': 'Pool', 'count': 'Count'}
    _toPy = {'Count': 'count', 'Pool': 'pool', 'Size': 'size'}
    def __init__(self, count, pool, size):
        '''
        count : int
        pool : str
        size : int
        '''
        self.count = count
        self.pool = pool
        self.size = size


class StorageDetails(Type):
    _toSchema = {'persistent': 'Persistent', 'status': 'status', 'kind': 'kind', 'ownertag': 'ownertag', 'storagetag': 'storagetag', 'attachments': 'attachments'}
    _toPy = {'status': 'status', 'kind': 'kind', 'ownertag': 'ownertag', 'storagetag': 'storagetag', 'Persistent': 'persistent', 'attachments': 'attachments'}
    def __init__(self, ownertag, kind, status, storagetag, attachments, persistent):
        '''
        ownertag : str
        kind : int
        status : ~EntityStatus
        storagetag : str
        attachments : typing.Mapping[str, ~StorageAttachmentDetails]
        persistent : bool
        '''
        self.ownertag = ownertag
        self.kind = kind
        self.status = status
        self.storagetag = storagetag
        self.attachments = attachments
        self.persistent = persistent


class StorageDetailsListResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : typing.Sequence[~StorageDetails]
        '''
        self.error = error
        self.result = result


class StorageDetailsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~StorageDetails
        '''
        self.error = error
        self.result = result


class StorageFilter(Type):
    _toSchema = {}
    _toPy = {}
    def __init__(self):
        '''

        '''
        pass


class StoragePool(Type):
    _toSchema = {'name': 'name', 'provider': 'provider', 'attrs': 'attrs'}
    _toPy = {'name': 'name', 'provider': 'provider', 'attrs': 'attrs'}
    def __init__(self, name, provider, attrs):
        '''
        name : str
        provider : str
        attrs : typing.Mapping[str, typing.Any]
        '''
        self.name = name
        self.provider = provider
        self.attrs = attrs


class StoragePoolFilter(Type):
    _toSchema = {'names': 'names', 'providers': 'providers'}
    _toPy = {'names': 'names', 'providers': 'providers'}
    def __init__(self, names, providers):
        '''
        names : typing.Sequence[str]
        providers : typing.Sequence[str]
        '''
        self.names = names
        self.providers = providers


class StoragePoolsResult(Type):
    _toSchema = {'storagepools': 'storagepools', 'error': 'error'}
    _toPy = {'storagepools': 'storagepools', 'error': 'error'}
    def __init__(self, storagepools, error):
        '''
        storagepools : typing.Sequence[~StoragePool]
        error : ~Error
        '''
        self.storagepools = storagepools
        self.error = error


class VolumeDetails(Type):
    _toSchema = {'info': 'info', 'volumetag': 'volumetag', 'status': 'status', 'machineattachments': 'machineattachments', 'storage': 'storage'}
    _toPy = {'info': 'info', 'volumetag': 'volumetag', 'status': 'status', 'machineattachments': 'machineattachments', 'storage': 'storage'}
    def __init__(self, info, volumetag, status, storage, machineattachments):
        '''
        info : ~VolumeInfo
        volumetag : str
        status : ~EntityStatus
        storage : ~StorageDetails
        machineattachments : typing.Mapping[str, ~VolumeAttachmentInfo]
        '''
        self.info = info
        self.volumetag = volumetag
        self.status = status
        self.storage = storage
        self.machineattachments = machineattachments


class VolumeDetailsListResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : typing.Sequence[~VolumeDetails]
        '''
        self.error = error
        self.result = result


class VolumeFilter(Type):
    _toSchema = {'machines': 'machines'}
    _toPy = {'machines': 'machines'}
    def __init__(self, machines):
        '''
        machines : typing.Sequence[str]
        '''
        self.machines = machines


class BlockDeviceResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~BlockDevice
        '''
        self.error = error
        self.result = result


class Filesystem(Type):
    _toSchema = {'info': 'info', 'volumetag': 'volumetag', 'filesystemtag': 'filesystemtag'}
    _toPy = {'info': 'info', 'volumetag': 'volumetag', 'filesystemtag': 'filesystemtag'}
    def __init__(self, info, volumetag, filesystemtag):
        '''
        info : ~FilesystemInfo
        volumetag : str
        filesystemtag : str
        '''
        self.info = info
        self.volumetag = volumetag
        self.filesystemtag = filesystemtag


class FilesystemAttachment(Type):
    _toSchema = {'info': 'info', 'filesystemtag': 'filesystemtag', 'machinetag': 'machinetag'}
    _toPy = {'info': 'info', 'filesystemtag': 'filesystemtag', 'machinetag': 'machinetag'}
    def __init__(self, info, machinetag, filesystemtag):
        '''
        info : ~FilesystemAttachmentInfo
        machinetag : str
        filesystemtag : str
        '''
        self.info = info
        self.machinetag = machinetag
        self.filesystemtag = filesystemtag


class FilesystemAttachmentParams(Type):
    _toSchema = {'provider': 'provider', 'machinetag': 'machinetag', 'filesystemid': 'filesystemid', 'instanceid': 'instanceid', 'read_only': 'read-only', 'mountpoint': 'mountpoint', 'filesystemtag': 'filesystemtag'}
    _toPy = {'provider': 'provider', 'machinetag': 'machinetag', 'filesystemid': 'filesystemid', 'instanceid': 'instanceid', 'read-only': 'read_only', 'mountpoint': 'mountpoint', 'filesystemtag': 'filesystemtag'}
    def __init__(self, provider, filesystemtag, filesystemid, instanceid, read_only, mountpoint, machinetag):
        '''
        provider : str
        filesystemtag : str
        filesystemid : str
        instanceid : str
        read_only : bool
        mountpoint : str
        machinetag : str
        '''
        self.provider = provider
        self.filesystemtag = filesystemtag
        self.filesystemid = filesystemid
        self.instanceid = instanceid
        self.read_only = read_only
        self.mountpoint = mountpoint
        self.machinetag = machinetag


class FilesystemAttachmentParamsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~FilesystemAttachmentParams
        '''
        self.error = error
        self.result = result


class FilesystemAttachmentResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~FilesystemAttachment
        '''
        self.error = error
        self.result = result


class FilesystemParams(Type):
    _toSchema = {'provider': 'provider', 'size': 'size', 'volumetag': 'volumetag', 'attachment': 'attachment', 'attributes': 'attributes', 'filesystemtag': 'filesystemtag', 'tags': 'tags'}
    _toPy = {'provider': 'provider', 'size': 'size', 'volumetag': 'volumetag', 'attachment': 'attachment', 'attributes': 'attributes', 'filesystemtag': 'filesystemtag', 'tags': 'tags'}
    def __init__(self, provider, size, volumetag, attachment, attributes, filesystemtag, tags):
        '''
        provider : str
        size : int
        volumetag : str
        attachment : ~FilesystemAttachmentParams
        attributes : typing.Mapping[str, typing.Any]
        filesystemtag : str
        tags : typing.Mapping[str, str]
        '''
        self.provider = provider
        self.size = size
        self.volumetag = volumetag
        self.attachment = attachment
        self.attributes = attributes
        self.filesystemtag = filesystemtag
        self.tags = tags


class FilesystemParamsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~FilesystemParams
        '''
        self.error = error
        self.result = result


class FilesystemResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~Filesystem
        '''
        self.error = error
        self.result = result


class MachineStorageIdsWatchResult(Type):
    _toSchema = {'changes': 'Changes', 'machinestorageidswatcherid': 'MachineStorageIdsWatcherId', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Changes': 'changes', 'MachineStorageIdsWatcherId': 'machinestorageidswatcherid'}
    def __init__(self, error, changes, machinestorageidswatcherid):
        '''
        error : ~Error
        changes : typing.Sequence[~MachineStorageId]
        machinestorageidswatcherid : str
        '''
        self.error = error
        self.changes = changes
        self.machinestorageidswatcherid = machinestorageidswatcherid


class VolumeAttachment(Type):
    _toSchema = {'info': 'info', 'volumetag': 'volumetag', 'machinetag': 'machinetag'}
    _toPy = {'info': 'info', 'volumetag': 'volumetag', 'machinetag': 'machinetag'}
    def __init__(self, info, volumetag, machinetag):
        '''
        info : ~VolumeAttachmentInfo
        volumetag : str
        machinetag : str
        '''
        self.info = info
        self.volumetag = volumetag
        self.machinetag = machinetag


class VolumeAttachmentParamsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~VolumeAttachmentParams
        '''
        self.error = error
        self.result = result


class VolumeAttachmentResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~VolumeAttachment
        '''
        self.error = error
        self.result = result


class VolumeParamsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~VolumeParams
        '''
        self.error = error
        self.result = result


class VolumeResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~Volume
        '''
        self.error = error
        self.result = result


class SpaceResult(Type):
    _toSchema = {'error': 'Error', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Error': 'error'}
    def __init__(self, tag, error):
        '''
        tag : str
        error : ~Error
        '''
        self.tag = tag
        self.error = error


class ZoneResult(Type):
    _toSchema = {'available': 'Available', 'name': 'Name', 'error': 'Error'}
    _toPy = {'Name': 'name', 'Error': 'error', 'Available': 'available'}
    def __init__(self, name, error, available):
        '''
        name : str
        error : ~Error
        available : bool
        '''
        self.name = name
        self.error = error
        self.available = available


class UndertakerModelInfo(Type):
    _toSchema = {'uuid': 'UUID', 'name': 'Name', 'issystem': 'IsSystem', 'life': 'Life', 'globalname': 'GlobalName'}
    _toPy = {'Name': 'name', 'GlobalName': 'globalname', 'IsSystem': 'issystem', 'UUID': 'uuid', 'Life': 'life'}
    def __init__(self, name, life, globalname, uuid, issystem):
        '''
        name : str
        life : str
        globalname : str
        uuid : str
        issystem : bool
        '''
        self.name = name
        self.life = life
        self.globalname = globalname
        self.uuid = uuid
        self.issystem = issystem


class CharmURL(Type):
    _toSchema = {'url': 'URL'}
    _toPy = {'URL': 'url'}
    def __init__(self, url):
        '''
        url : str
        '''
        self.url = url


class ConfigSettingsResult(Type):
    _toSchema = {'settings': 'Settings', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Settings': 'settings'}
    def __init__(self, error, settings):
        '''
        error : ~Error
        settings : typing.Mapping[str, typing.Any]
        '''
        self.error = error
        self.settings = settings


class Endpoint(Type):
    _toSchema = {'servicename': 'ServiceName', 'relation': 'Relation'}
    _toPy = {'Relation': 'relation', 'ServiceName': 'servicename'}
    def __init__(self, relation, servicename):
        '''
        relation : ~Relation
        servicename : str
        '''
        self.relation = relation
        self.servicename = servicename


class EntityCharmURL(Type):
    _toSchema = {'charmurl': 'CharmURL', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'CharmURL': 'charmurl'}
    def __init__(self, tag, charmurl):
        '''
        tag : str
        charmurl : str
        '''
        self.tag = tag
        self.charmurl = charmurl


class EntityPortRange(Type):
    _toSchema = {'toport': 'ToPort', 'protocol': 'Protocol', 'fromport': 'FromPort', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'FromPort': 'fromport', 'ToPort': 'toport', 'Protocol': 'protocol'}
    def __init__(self, tag, fromport, toport, protocol):
        '''
        tag : str
        fromport : int
        toport : int
        protocol : str
        '''
        self.tag = tag
        self.fromport = fromport
        self.toport = toport
        self.protocol = protocol


class GetLeadershipSettingsResult(Type):
    _toSchema = {'settings': 'Settings', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Settings': 'settings'}
    def __init__(self, error, settings):
        '''
        error : ~Error
        settings : typing.Mapping[str, str]
        '''
        self.error = error
        self.settings = settings


class IntResult(Type):
    _toSchema = {'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : int
        '''
        self.error = error
        self.result = result


class MergeLeadershipSettingsParam(Type):
    _toSchema = {'servicetag': 'ServiceTag', 'settings': 'Settings'}
    _toPy = {'ServiceTag': 'servicetag', 'Settings': 'settings'}
    def __init__(self, servicetag, settings):
        '''
        servicetag : str
        settings : typing.Mapping[str, str]
        '''
        self.servicetag = servicetag
        self.settings = settings


class RelationResult(Type):
    _toSchema = {'key': 'Key', 'id_': 'Id', 'life': 'Life', 'error': 'Error', 'endpoint': 'Endpoint'}
    _toPy = {'Life': 'life', 'Error': 'error', 'Endpoint': 'endpoint', 'Key': 'key', 'Id': 'id_'}
    def __init__(self, life, error, endpoint, key, id_):
        '''
        life : str
        error : ~Error
        endpoint : ~Endpoint
        key : str
        id_ : int
        '''
        self.life = life
        self.error = error
        self.endpoint = endpoint
        self.key = key
        self.id_ = id_


class RelationUnit(Type):
    _toSchema = {'relation': 'Relation', 'unit': 'Unit'}
    _toPy = {'Relation': 'relation', 'Unit': 'unit'}
    def __init__(self, relation, unit):
        '''
        relation : str
        unit : str
        '''
        self.relation = relation
        self.unit = unit


class RelationUnitPair(Type):
    _toSchema = {'relation': 'Relation', 'remoteunit': 'RemoteUnit', 'localunit': 'LocalUnit'}
    _toPy = {'LocalUnit': 'localunit', 'RemoteUnit': 'remoteunit', 'Relation': 'relation'}
    def __init__(self, localunit, remoteunit, relation):
        '''
        localunit : str
        remoteunit : str
        relation : str
        '''
        self.localunit = localunit
        self.remoteunit = remoteunit
        self.relation = relation


class RelationUnitSettings(Type):
    _toSchema = {'settings': 'Settings', 'relation': 'Relation', 'unit': 'Unit'}
    _toPy = {'Relation': 'relation', 'Unit': 'unit', 'Settings': 'settings'}
    def __init__(self, relation, unit, settings):
        '''
        relation : str
        unit : str
        settings : typing.Mapping[str, str]
        '''
        self.relation = relation
        self.unit = unit
        self.settings = settings


class RelationUnitsWatchResult(Type):
    _toSchema = {'changes': 'Changes', 'relationunitswatcherid': 'RelationUnitsWatcherId', 'error': 'Error'}
    _toPy = {'Error': 'error', 'RelationUnitsWatcherId': 'relationunitswatcherid', 'Changes': 'changes'}
    def __init__(self, error, relationunitswatcherid, changes):
        '''
        error : ~Error
        relationunitswatcherid : str
        changes : ~RelationUnitsChange
        '''
        self.error = error
        self.relationunitswatcherid = relationunitswatcherid
        self.changes = changes


class ResolvedModeResult(Type):
    _toSchema = {'mode': 'Mode', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Mode': 'mode'}
    def __init__(self, error, mode):
        '''
        error : ~Error
        mode : str
        '''
        self.error = error
        self.mode = mode


class ServiceStatusResult(Type):
    _toSchema = {'units': 'Units', 'service': 'Service', 'error': 'Error'}
    _toPy = {'Units': 'units', 'Error': 'error', 'Service': 'service'}
    def __init__(self, units, error, service):
        '''
        units : typing.Mapping[str, ~StatusResult]
        error : ~Error
        service : ~StatusResult
        '''
        self.units = units
        self.error = error
        self.service = service


class SettingsResult(Type):
    _toSchema = {'settings': 'Settings', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Settings': 'settings'}
    def __init__(self, error, settings):
        '''
        error : ~Error
        settings : typing.Mapping[str, str]
        '''
        self.error = error
        self.settings = settings


class StorageAttachment(Type):
    _toSchema = {'unittag': 'UnitTag', 'ownertag': 'OwnerTag', 'kind': 'Kind', 'storagetag': 'StorageTag', 'location': 'Location', 'life': 'Life'}
    _toPy = {'Kind': 'kind', 'StorageTag': 'storagetag', 'Location': 'location', 'Life': 'life', 'OwnerTag': 'ownertag', 'UnitTag': 'unittag'}
    def __init__(self, kind, storagetag, location, life, ownertag, unittag):
        '''
        kind : int
        storagetag : str
        location : str
        life : str
        ownertag : str
        unittag : str
        '''
        self.kind = kind
        self.storagetag = storagetag
        self.location = location
        self.life = life
        self.ownertag = ownertag
        self.unittag = unittag


class StorageAttachmentId(Type):
    _toSchema = {'unittag': 'unittag', 'storagetag': 'storagetag'}
    _toPy = {'unittag': 'unittag', 'storagetag': 'storagetag'}
    def __init__(self, unittag, storagetag):
        '''
        unittag : str
        storagetag : str
        '''
        self.unittag = unittag
        self.storagetag = storagetag


class StorageAttachmentIds(Type):
    _toSchema = {'ids': 'ids'}
    _toPy = {'ids': 'ids'}
    def __init__(self, ids):
        '''
        ids : typing.Sequence[~StorageAttachmentId]
        '''
        self.ids = ids


class StorageAttachmentIdsResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~StorageAttachmentIds
        '''
        self.error = error
        self.result = result


class StorageAttachmentResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~StorageAttachment
        '''
        self.error = error
        self.result = result


class StringBoolResult(Type):
    _toSchema = {'ok': 'Ok', 'error': 'Error', 'result': 'Result'}
    _toPy = {'Error': 'error', 'Ok': 'ok', 'Result': 'result'}
    def __init__(self, error, ok, result):
        '''
        error : ~Error
        ok : bool
        result : str
        '''
        self.error = error
        self.ok = ok
        self.result = result


class UnitNetworkConfig(Type):
    _toSchema = {'unittag': 'UnitTag', 'bindingname': 'BindingName'}
    _toPy = {'BindingName': 'bindingname', 'UnitTag': 'unittag'}
    def __init__(self, bindingname, unittag):
        '''
        bindingname : str
        unittag : str
        '''
        self.bindingname = bindingname
        self.unittag = unittag


class UnitNetworkConfigResult(Type):
    _toSchema = {'info': 'Info', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Info': 'info'}
    def __init__(self, error, info):
        '''
        error : ~Error
        info : typing.Sequence[~NetworkConfig]
        '''
        self.error = error
        self.info = info


class EntityVersion(Type):
    _toSchema = {'tools': 'Tools', 'tag': 'Tag'}
    _toPy = {'Tag': 'tag', 'Tools': 'tools'}
    def __init__(self, tag, tools):
        '''
        tag : str
        tools : ~Version
        '''
        self.tag = tag
        self.tools = tools


class VersionResult(Type):
    _toSchema = {'version': 'Version', 'error': 'Error'}
    _toPy = {'Error': 'error', 'Version': 'version'}
    def __init__(self, error, version):
        '''
        error : ~Error
        version : ~Number
        '''
        self.error = error
        self.version = version


class AddUser(Type):
    _toSchema = {'password': 'password', 'username': 'username', 'shared_model_tags': 'shared-model-tags', 'display_name': 'display-name', 'model_access_permission': 'model-access-permission'}
    _toPy = {'password': 'password', 'username': 'username', 'model-access-permission': 'model_access_permission', 'display-name': 'display_name', 'shared-model-tags': 'shared_model_tags'}
    def __init__(self, username, password, shared_model_tags, model_access_permission, display_name):
        '''
        username : str
        password : str
        shared_model_tags : typing.Sequence[str]
        model_access_permission : str
        display_name : str
        '''
        self.username = username
        self.password = password
        self.shared_model_tags = shared_model_tags
        self.model_access_permission = model_access_permission
        self.display_name = display_name


class AddUserResult(Type):
    _toSchema = {'tag': 'tag', 'error': 'error', 'secret_key': 'secret-key'}
    _toPy = {'error': 'error', 'secret-key': 'secret_key', 'tag': 'tag'}
    def __init__(self, error, secret_key, tag):
        '''
        error : ~Error
        secret_key : typing.Sequence[int]
        tag : str
        '''
        self.error = error
        self.secret_key = secret_key
        self.tag = tag


class MacaroonResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~Macaroon
        '''
        self.error = error
        self.result = result


class UserInfo(Type):
    _toSchema = {'disabled': 'disabled', 'date_created': 'date-created', 'created_by': 'created-by', 'last_connection': 'last-connection', 'username': 'username', 'display_name': 'display-name'}
    _toPy = {'disabled': 'disabled', 'created-by': 'created_by', 'username': 'username', 'last-connection': 'last_connection', 'date-created': 'date_created', 'display-name': 'display_name'}
    def __init__(self, disabled, username, created_by, last_connection, date_created, display_name):
        '''
        disabled : bool
        username : str
        created_by : str
        last_connection : str
        date_created : str
        display_name : str
        '''
        self.disabled = disabled
        self.username = username
        self.created_by = created_by
        self.last_connection = last_connection
        self.date_created = date_created
        self.display_name = display_name


class UserInfoResult(Type):
    _toSchema = {'error': 'error', 'result': 'result'}
    _toPy = {'error': 'error', 'result': 'result'}
    def __init__(self, error, result):
        '''
        error : ~Error
        result : ~UserInfo
        '''
        self.error = error
        self.result = result


class Action(Type):
    name = 'Action'
    version = 1
    schema =     {'definitions': {'Action': {'additionalProperties': False,
                                'properties': {'name': {'type': 'string'},
                                               'parameters': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                               'receiver': {'type': 'string'},
                                               'tag': {'type': 'string'}},
                                'required': ['tag', 'receiver', 'name'],
                                'type': 'object'},
                     'ActionResult': {'additionalProperties': False,
                                      'properties': {'action': {'$ref': '#/definitions/Action'},
                                                     'completed': {'format': 'date-time',
                                                                   'type': 'string'},
                                                     'enqueued': {'format': 'date-time',
                                                                  'type': 'string'},
                                                     'error': {'$ref': '#/definitions/Error'},
                                                     'message': {'type': 'string'},
                                                     'output': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                             'type': 'object'}},
                                                                'type': 'object'},
                                                     'started': {'format': 'date-time',
                                                                 'type': 'string'},
                                                     'status': {'type': 'string'}},
                                      'type': 'object'},
                     'ActionResults': {'additionalProperties': False,
                                       'properties': {'results': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'Actions': {'additionalProperties': False,
                                 'properties': {'actions': {'items': {'$ref': '#/definitions/Action'},
                                                            'type': 'array'}},
                                 'type': 'object'},
                     'ActionsByName': {'additionalProperties': False,
                                       'properties': {'actions': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                  'type': 'array'},
                                                      'error': {'$ref': '#/definitions/Error'},
                                                      'name': {'type': 'string'}},
                                       'type': 'object'},
                     'ActionsByNames': {'additionalProperties': False,
                                        'properties': {'actions': {'items': {'$ref': '#/definitions/ActionsByName'},
                                                                   'type': 'array'}},
                                        'type': 'object'},
                     'ActionsByReceiver': {'additionalProperties': False,
                                           'properties': {'actions': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                      'type': 'array'},
                                                          'error': {'$ref': '#/definitions/Error'},
                                                          'receiver': {'type': 'string'}},
                                           'type': 'object'},
                     'ActionsByReceivers': {'additionalProperties': False,
                                            'properties': {'actions': {'items': {'$ref': '#/definitions/ActionsByReceiver'},
                                                                       'type': 'array'}},
                                            'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'FindActionsByNames': {'additionalProperties': False,
                                            'properties': {'names': {'items': {'type': 'string'},
                                                                     'type': 'array'}},
                                            'type': 'object'},
                     'FindTags': {'additionalProperties': False,
                                  'properties': {'prefixes': {'items': {'type': 'string'},
                                                              'type': 'array'}},
                                  'required': ['prefixes'],
                                  'type': 'object'},
                     'FindTagsResults': {'additionalProperties': False,
                                         'properties': {'matches': {'patternProperties': {'.*': {'items': {'$ref': '#/definitions/Entity'},
                                                                                                 'type': 'array'}},
                                                                    'type': 'object'}},
                                         'required': ['matches'],
                                         'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'RunParams': {'additionalProperties': False,
                                   'properties': {'Commands': {'type': 'string'},
                                                  'Machines': {'items': {'type': 'string'},
                                                               'type': 'array'},
                                                  'Services': {'items': {'type': 'string'},
                                                               'type': 'array'},
                                                  'Timeout': {'type': 'integer'},
                                                  'Units': {'items': {'type': 'string'},
                                                            'type': 'array'}},
                                   'required': ['Commands',
                                                'Timeout',
                                                'Machines',
                                                'Services',
                                                'Units'],
                                   'type': 'object'},
                     'ServiceCharmActionsResult': {'additionalProperties': False,
                                                   'properties': {'actions': {'$ref': '#/definitions/Actions'},
                                                                  'error': {'$ref': '#/definitions/Error'},
                                                                  'servicetag': {'type': 'string'}},
                                                   'type': 'object'},
                     'ServicesCharmActionsResults': {'additionalProperties': False,
                                                     'properties': {'results': {'items': {'$ref': '#/definitions/ServiceCharmActionsResult'},
                                                                                'type': 'array'}},
                                                     'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Actions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ActionResults'}},
                                'type': 'object'},
                    'Cancel': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/ActionResults'}},
                               'type': 'object'},
                    'Enqueue': {'properties': {'Params': {'$ref': '#/definitions/Actions'},
                                               'Result': {'$ref': '#/definitions/ActionResults'}},
                                'type': 'object'},
                    'FindActionTagsByPrefix': {'properties': {'Params': {'$ref': '#/definitions/FindTags'},
                                                              'Result': {'$ref': '#/definitions/FindTagsResults'}},
                                               'type': 'object'},
                    'FindActionsByNames': {'properties': {'Params': {'$ref': '#/definitions/FindActionsByNames'},
                                                          'Result': {'$ref': '#/definitions/ActionsByNames'}},
                                           'type': 'object'},
                    'ListAll': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ActionsByReceivers'}},
                                'type': 'object'},
                    'ListCompleted': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/ActionsByReceivers'}},
                                      'type': 'object'},
                    'ListPending': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ActionsByReceivers'}},
                                    'type': 'object'},
                    'ListRunning': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ActionsByReceivers'}},
                                    'type': 'object'},
                    'Run': {'properties': {'Params': {'$ref': '#/definitions/RunParams'},
                                           'Result': {'$ref': '#/definitions/ActionResults'}},
                            'type': 'object'},
                    'RunOnAllMachines': {'properties': {'Params': {'$ref': '#/definitions/RunParams'},
                                                        'Result': {'$ref': '#/definitions/ActionResults'}},
                                         'type': 'object'},
                    'ServicesCharmActions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                            'Result': {'$ref': '#/definitions/ServicesCharmActionsResults'}},
                                             'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ActionResults)
    async def Actions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='Actions', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Actions)



    #@ReturnMapping(ActionResults)
    async def Cancel(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='Cancel', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Cancel)



    #@ReturnMapping(ActionResults)
    async def Enqueue(self, actions):
        '''
        actions : typing.Sequence[~Action]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='Enqueue', Version=1, Params=params)
        params['actions'] = actions
        reply = await self.rpc(msg)
        return self._map(reply, Enqueue)



    #@ReturnMapping(FindTagsResults)
    async def FindActionTagsByPrefix(self, prefixes):
        '''
        prefixes : typing.Sequence[str]
        Returns -> typing.Sequence[~Entity]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='FindActionTagsByPrefix', Version=1, Params=params)
        params['prefixes'] = prefixes
        reply = await self.rpc(msg)
        return self._map(reply, FindActionTagsByPrefix)



    #@ReturnMapping(ActionsByNames)
    async def FindActionsByNames(self, names):
        '''
        names : typing.Sequence[str]
        Returns -> typing.Sequence[~ActionsByName]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='FindActionsByNames', Version=1, Params=params)
        params['names'] = names
        reply = await self.rpc(msg)
        return self._map(reply, FindActionsByNames)



    #@ReturnMapping(ActionsByReceivers)
    async def ListAll(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionsByReceiver]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='ListAll', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ListAll)



    #@ReturnMapping(ActionsByReceivers)
    async def ListCompleted(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionsByReceiver]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='ListCompleted', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ListCompleted)



    #@ReturnMapping(ActionsByReceivers)
    async def ListPending(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionsByReceiver]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='ListPending', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ListPending)



    #@ReturnMapping(ActionsByReceivers)
    async def ListRunning(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionsByReceiver]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='ListRunning', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ListRunning)



    #@ReturnMapping(ActionResults)
    async def Run(self, services, timeout, units, commands, machines):
        '''
        services : typing.Sequence[str]
        timeout : int
        units : typing.Sequence[str]
        commands : str
        machines : typing.Sequence[str]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='Run', Version=1, Params=params)
        params['Services'] = services
        params['Timeout'] = timeout
        params['Units'] = units
        params['Commands'] = commands
        params['Machines'] = machines
        reply = await self.rpc(msg)
        return self._map(reply, Run)



    #@ReturnMapping(ActionResults)
    async def RunOnAllMachines(self, services, timeout, units, commands, machines):
        '''
        services : typing.Sequence[str]
        timeout : int
        units : typing.Sequence[str]
        commands : str
        machines : typing.Sequence[str]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='RunOnAllMachines', Version=1, Params=params)
        params['Services'] = services
        params['Timeout'] = timeout
        params['Units'] = units
        params['Commands'] = commands
        params['Machines'] = machines
        reply = await self.rpc(msg)
        return self._map(reply, RunOnAllMachines)



    #@ReturnMapping(ServicesCharmActionsResults)
    async def ServicesCharmActions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ServiceCharmActionsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Action', Request='ServicesCharmActions', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ServicesCharmActions)


class Addresser(Type):
    name = 'Addresser'
    version = 2
    schema =     {'definitions': {'BoolResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Result': {'type': 'boolean'}},
                                    'required': ['Error', 'Result'],
                                    'type': 'object'},
                     'EntitiesWatchResult': {'additionalProperties': False,
                                             'properties': {'Changes': {'items': {'type': 'string'},
                                                                        'type': 'array'},
                                                            'EntityWatcherId': {'type': 'string'},
                                                            'Error': {'$ref': '#/definitions/Error'}},
                                             'required': ['EntityWatcherId',
                                                          'Changes',
                                                          'Error'],
                                             'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'CanDeallocateAddresses': {'properties': {'Result': {'$ref': '#/definitions/BoolResult'}},
                                               'type': 'object'},
                    'CleanupIPAddresses': {'properties': {'Result': {'$ref': '#/definitions/ErrorResult'}},
                                           'type': 'object'},
                    'WatchIPAddresses': {'properties': {'Result': {'$ref': '#/definitions/EntitiesWatchResult'}},
                                         'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(BoolResult)
    async def CanDeallocateAddresses(self):
        '''

        Returns -> typing.Union[~Error, bool]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Addresser', Request='CanDeallocateAddresses', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CanDeallocateAddresses)



    #@ReturnMapping(ErrorResult)
    async def CleanupIPAddresses(self):
        '''

        Returns -> ~Error
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Addresser', Request='CleanupIPAddresses', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CleanupIPAddresses)



    #@ReturnMapping(EntitiesWatchResult)
    async def WatchIPAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Addresser', Request='WatchIPAddresses', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchIPAddresses)


class Agent(Type):
    name = 'Agent'
    version = 2
    schema =     {'definitions': {'AgentGetEntitiesResult': {'additionalProperties': False,
                                                'properties': {'ContainerType': {'type': 'string'},
                                                               'Error': {'$ref': '#/definitions/Error'},
                                                               'Jobs': {'items': {'type': 'string'},
                                                                        'type': 'array'},
                                                               'Life': {'type': 'string'}},
                                                'required': ['Life',
                                                             'Jobs',
                                                             'ContainerType',
                                                             'Error'],
                                                'type': 'object'},
                     'AgentGetEntitiesResults': {'additionalProperties': False,
                                                 'properties': {'Entities': {'items': {'$ref': '#/definitions/AgentGetEntitiesResult'},
                                                                             'type': 'array'}},
                                                 'required': ['Entities'],
                                                 'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityPassword': {'additionalProperties': False,
                                        'properties': {'Password': {'type': 'string'},
                                                       'Tag': {'type': 'string'}},
                                        'required': ['Tag', 'Password'],
                                        'type': 'object'},
                     'EntityPasswords': {'additionalProperties': False,
                                         'properties': {'Changes': {'items': {'$ref': '#/definitions/EntityPassword'},
                                                                    'type': 'array'}},
                                         'required': ['Changes'],
                                         'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'IsMasterResult': {'additionalProperties': False,
                                        'properties': {'Master': {'type': 'boolean'}},
                                        'required': ['Master'],
                                        'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'StateServingInfo': {'additionalProperties': False,
                                          'properties': {'APIPort': {'type': 'integer'},
                                                         'CAPrivateKey': {'type': 'string'},
                                                         'Cert': {'type': 'string'},
                                                         'PrivateKey': {'type': 'string'},
                                                         'SharedSecret': {'type': 'string'},
                                                         'StatePort': {'type': 'integer'},
                                                         'SystemIdentity': {'type': 'string'}},
                                          'required': ['APIPort',
                                                       'StatePort',
                                                       'Cert',
                                                       'PrivateKey',
                                                       'CAPrivateKey',
                                                       'SharedSecret',
                                                       'SystemIdentity'],
                                          'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ClearReboot': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'GetEntities': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/AgentGetEntitiesResults'}},
                                    'type': 'object'},
                    'IsMaster': {'properties': {'Result': {'$ref': '#/definitions/IsMasterResult'}},
                                 'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'SetPasswords': {'properties': {'Params': {'$ref': '#/definitions/EntityPasswords'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'StateServingInfo': {'properties': {'Result': {'$ref': '#/definitions/StateServingInfo'}},
                                         'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def ClearReboot(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='ClearReboot', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ClearReboot)



    #@ReturnMapping(AgentGetEntitiesResults)
    async def GetEntities(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~AgentGetEntitiesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='GetEntities', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetEntities)



    #@ReturnMapping(IsMasterResult)
    async def IsMaster(self):
        '''

        Returns -> bool
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='IsMaster', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, IsMaster)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(ErrorResults)
    async def SetPasswords(self, changes):
        '''
        changes : typing.Sequence[~EntityPassword]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='SetPasswords', Version=2, Params=params)
        params['Changes'] = changes
        reply = await self.rpc(msg)
        return self._map(reply, SetPasswords)



    #@ReturnMapping(StateServingInfo)
    async def StateServingInfo(self):
        '''

        Returns -> typing.Union[int, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='StateServingInfo', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, StateServingInfo)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Agent', Request='WatchForModelConfigChanges', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)


class AgentTools(Type):
    name = 'AgentTools'
    version = 1
    schema =     {'properties': {'UpdateToolsAvailable': {'type': 'object'}}, 'type': 'object'}
    

    #@ReturnMapping(None)
    async def UpdateToolsAvailable(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='AgentTools', Request='UpdateToolsAvailable', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, UpdateToolsAvailable)


class AllModelWatcher(Type):
    name = 'AllModelWatcher'
    version = 2
    schema =     {'definitions': {'AllWatcherNextResults': {'additionalProperties': False,
                                               'properties': {'Deltas': {'items': {'$ref': '#/definitions/Delta'},
                                                                         'type': 'array'}},
                                               'required': ['Deltas'],
                                               'type': 'object'},
                     'Delta': {'additionalProperties': False,
                               'properties': {'Entity': {'additionalProperties': True,
                                                         'type': 'object'},
                                              'Removed': {'type': 'boolean'}},
                               'required': ['Removed', 'Entity'],
                               'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/AllWatcherNextResults'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AllWatcherNextResults)
    async def Next(self):
        '''

        Returns -> typing.Sequence[~Delta]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='AllModelWatcher', Request='Next', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='AllModelWatcher', Request='Stop', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class AllWatcher(Type):
    name = 'AllWatcher'
    version = 1
    schema =     {'definitions': {'AllWatcherNextResults': {'additionalProperties': False,
                                               'properties': {'Deltas': {'items': {'$ref': '#/definitions/Delta'},
                                                                         'type': 'array'}},
                                               'required': ['Deltas'],
                                               'type': 'object'},
                     'Delta': {'additionalProperties': False,
                               'properties': {'Entity': {'additionalProperties': True,
                                                         'type': 'object'},
                                              'Removed': {'type': 'boolean'}},
                               'required': ['Removed', 'Entity'],
                               'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/AllWatcherNextResults'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AllWatcherNextResults)
    async def Next(self):
        '''

        Returns -> typing.Sequence[~Delta]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='AllWatcher', Request='Next', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='AllWatcher', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Annotations(Type):
    name = 'Annotations'
    version = 2
    schema =     {'definitions': {'AnnotationsGetResult': {'additionalProperties': False,
                                              'properties': {'Annotations': {'patternProperties': {'.*': {'type': 'string'}},
                                                                             'type': 'object'},
                                                             'EntityTag': {'type': 'string'},
                                                             'Error': {'$ref': '#/definitions/ErrorResult'}},
                                              'required': ['EntityTag',
                                                           'Annotations',
                                                           'Error'],
                                              'type': 'object'},
                     'AnnotationsGetResults': {'additionalProperties': False,
                                               'properties': {'Results': {'items': {'$ref': '#/definitions/AnnotationsGetResult'},
                                                                          'type': 'array'}},
                                               'required': ['Results'],
                                               'type': 'object'},
                     'AnnotationsSet': {'additionalProperties': False,
                                        'properties': {'Annotations': {'items': {'$ref': '#/definitions/EntityAnnotations'},
                                                                       'type': 'array'}},
                                        'required': ['Annotations'],
                                        'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityAnnotations': {'additionalProperties': False,
                                           'properties': {'Annotations': {'patternProperties': {'.*': {'type': 'string'}},
                                                                          'type': 'object'},
                                                          'EntityTag': {'type': 'string'}},
                                           'required': ['EntityTag', 'Annotations'],
                                           'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Get': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                           'Result': {'$ref': '#/definitions/AnnotationsGetResults'}},
                            'type': 'object'},
                    'Set': {'properties': {'Params': {'$ref': '#/definitions/AnnotationsSet'},
                                           'Result': {'$ref': '#/definitions/ErrorResults'}},
                            'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AnnotationsGetResults)
    async def Get(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~AnnotationsGetResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Annotations', Request='Get', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Get)



    #@ReturnMapping(ErrorResults)
    async def Set(self, annotations):
        '''
        annotations : typing.Sequence[~EntityAnnotations]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Annotations', Request='Set', Version=2, Params=params)
        params['Annotations'] = annotations
        reply = await self.rpc(msg)
        return self._map(reply, Set)


class Backups(Type):
    name = 'Backups'
    version = 1
    schema =     {'definitions': {'BackupsCreateArgs': {'additionalProperties': False,
                                           'properties': {'Notes': {'type': 'string'}},
                                           'required': ['Notes'],
                                           'type': 'object'},
                     'BackupsInfoArgs': {'additionalProperties': False,
                                         'properties': {'ID': {'type': 'string'}},
                                         'required': ['ID'],
                                         'type': 'object'},
                     'BackupsListArgs': {'additionalProperties': False,
                                         'type': 'object'},
                     'BackupsListResult': {'additionalProperties': False,
                                           'properties': {'List': {'items': {'$ref': '#/definitions/BackupsMetadataResult'},
                                                                   'type': 'array'}},
                                           'required': ['List'],
                                           'type': 'object'},
                     'BackupsMetadataResult': {'additionalProperties': False,
                                               'properties': {'CACert': {'type': 'string'},
                                                              'CAPrivateKey': {'type': 'string'},
                                                              'Checksum': {'type': 'string'},
                                                              'ChecksumFormat': {'type': 'string'},
                                                              'Finished': {'format': 'date-time',
                                                                           'type': 'string'},
                                                              'Hostname': {'type': 'string'},
                                                              'ID': {'type': 'string'},
                                                              'Machine': {'type': 'string'},
                                                              'Model': {'type': 'string'},
                                                              'Notes': {'type': 'string'},
                                                              'Size': {'type': 'integer'},
                                                              'Started': {'format': 'date-time',
                                                                          'type': 'string'},
                                                              'Stored': {'format': 'date-time',
                                                                         'type': 'string'},
                                                              'Version': {'$ref': '#/definitions/Number'}},
                                               'required': ['ID',
                                                            'Checksum',
                                                            'ChecksumFormat',
                                                            'Size',
                                                            'Stored',
                                                            'Started',
                                                            'Finished',
                                                            'Notes',
                                                            'Model',
                                                            'Machine',
                                                            'Hostname',
                                                            'Version',
                                                            'CACert',
                                                            'CAPrivateKey'],
                                               'type': 'object'},
                     'BackupsRemoveArgs': {'additionalProperties': False,
                                           'properties': {'ID': {'type': 'string'}},
                                           'required': ['ID'],
                                           'type': 'object'},
                     'Number': {'additionalProperties': False,
                                'properties': {'Build': {'type': 'integer'},
                                               'Major': {'type': 'integer'},
                                               'Minor': {'type': 'integer'},
                                               'Patch': {'type': 'integer'},
                                               'Tag': {'type': 'string'}},
                                'required': ['Major',
                                             'Minor',
                                             'Tag',
                                             'Patch',
                                             'Build'],
                                'type': 'object'},
                     'RestoreArgs': {'additionalProperties': False,
                                     'properties': {'BackupId': {'type': 'string'}},
                                     'required': ['BackupId'],
                                     'type': 'object'}},
     'properties': {'Create': {'properties': {'Params': {'$ref': '#/definitions/BackupsCreateArgs'},
                                              'Result': {'$ref': '#/definitions/BackupsMetadataResult'}},
                               'type': 'object'},
                    'FinishRestore': {'type': 'object'},
                    'Info': {'properties': {'Params': {'$ref': '#/definitions/BackupsInfoArgs'},
                                            'Result': {'$ref': '#/definitions/BackupsMetadataResult'}},
                             'type': 'object'},
                    'List': {'properties': {'Params': {'$ref': '#/definitions/BackupsListArgs'},
                                            'Result': {'$ref': '#/definitions/BackupsListResult'}},
                             'type': 'object'},
                    'PrepareRestore': {'type': 'object'},
                    'Remove': {'properties': {'Params': {'$ref': '#/definitions/BackupsRemoveArgs'}},
                               'type': 'object'},
                    'Restore': {'properties': {'Params': {'$ref': '#/definitions/RestoreArgs'}},
                                'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(BackupsMetadataResult)
    async def Create(self, notes):
        '''
        notes : str
        Returns -> typing.Union[str, ~Number, int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='Create', Version=1, Params=params)
        params['Notes'] = notes
        reply = await self.rpc(msg)
        return self._map(reply, Create)



    #@ReturnMapping(None)
    async def FinishRestore(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='FinishRestore', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, FinishRestore)



    #@ReturnMapping(BackupsMetadataResult)
    async def Info(self, id_):
        '''
        id_ : str
        Returns -> typing.Union[str, ~Number, int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='Info', Version=1, Params=params)
        params['ID'] = id_
        reply = await self.rpc(msg)
        return self._map(reply, Info)



    #@ReturnMapping(BackupsListResult)
    async def List(self):
        '''

        Returns -> typing.Sequence[~BackupsMetadataResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='List', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, List)



    #@ReturnMapping(None)
    async def PrepareRestore(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='PrepareRestore', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, PrepareRestore)



    #@ReturnMapping(None)
    async def Remove(self, id_):
        '''
        id_ : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='Remove', Version=1, Params=params)
        params['ID'] = id_
        reply = await self.rpc(msg)
        return self._map(reply, Remove)



    #@ReturnMapping(None)
    async def Restore(self, backupid):
        '''
        backupid : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Backups', Request='Restore', Version=1, Params=params)
        params['BackupId'] = backupid
        reply = await self.rpc(msg)
        return self._map(reply, Restore)


class Block(Type):
    name = 'Block'
    version = 2
    schema =     {'definitions': {'Block': {'additionalProperties': False,
                               'properties': {'id': {'type': 'string'},
                                              'message': {'type': 'string'},
                                              'tag': {'type': 'string'},
                                              'type': {'type': 'string'}},
                               'required': ['id', 'tag', 'type'],
                               'type': 'object'},
                     'BlockResult': {'additionalProperties': False,
                                     'properties': {'error': {'$ref': '#/definitions/Error'},
                                                    'result': {'$ref': '#/definitions/Block'}},
                                     'required': ['result'],
                                     'type': 'object'},
                     'BlockResults': {'additionalProperties': False,
                                      'properties': {'results': {'items': {'$ref': '#/definitions/BlockResult'},
                                                                 'type': 'array'}},
                                      'type': 'object'},
                     'BlockSwitchParams': {'additionalProperties': False,
                                           'properties': {'message': {'type': 'string'},
                                                          'type': {'type': 'string'}},
                                           'required': ['type'],
                                           'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'List': {'properties': {'Result': {'$ref': '#/definitions/BlockResults'}},
                             'type': 'object'},
                    'SwitchBlockOff': {'properties': {'Params': {'$ref': '#/definitions/BlockSwitchParams'},
                                                      'Result': {'$ref': '#/definitions/ErrorResult'}},
                                       'type': 'object'},
                    'SwitchBlockOn': {'properties': {'Params': {'$ref': '#/definitions/BlockSwitchParams'},
                                                     'Result': {'$ref': '#/definitions/ErrorResult'}},
                                      'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(BlockResults)
    async def List(self):
        '''

        Returns -> typing.Sequence[~BlockResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Block', Request='List', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, List)



    #@ReturnMapping(ErrorResult)
    async def SwitchBlockOff(self, message, type_):
        '''
        message : str
        type_ : str
        Returns -> ~Error
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Block', Request='SwitchBlockOff', Version=2, Params=params)
        params['message'] = message
        params['type'] = type_
        reply = await self.rpc(msg)
        return self._map(reply, SwitchBlockOff)



    #@ReturnMapping(ErrorResult)
    async def SwitchBlockOn(self, message, type_):
        '''
        message : str
        type_ : str
        Returns -> ~Error
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Block', Request='SwitchBlockOn', Version=2, Params=params)
        params['message'] = message
        params['type'] = type_
        reply = await self.rpc(msg)
        return self._map(reply, SwitchBlockOn)


class CharmRevisionUpdater(Type):
    name = 'CharmRevisionUpdater'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'UpdateLatestRevisions': {'properties': {'Result': {'$ref': '#/definitions/ErrorResult'}},
                                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResult)
    async def UpdateLatestRevisions(self):
        '''

        Returns -> ~Error
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='CharmRevisionUpdater', Request='UpdateLatestRevisions', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, UpdateLatestRevisions)


class Charms(Type):
    name = 'Charms'
    version = 2
    schema =     {'definitions': {'CharmInfo': {'additionalProperties': False,
                                   'properties': {'CharmURL': {'type': 'string'}},
                                   'required': ['CharmURL'],
                                   'type': 'object'},
                     'CharmsList': {'additionalProperties': False,
                                    'properties': {'Names': {'items': {'type': 'string'},
                                                             'type': 'array'}},
                                    'required': ['Names'],
                                    'type': 'object'},
                     'CharmsListResult': {'additionalProperties': False,
                                          'properties': {'CharmURLs': {'items': {'type': 'string'},
                                                                       'type': 'array'}},
                                          'required': ['CharmURLs'],
                                          'type': 'object'},
                     'IsMeteredResult': {'additionalProperties': False,
                                         'properties': {'Metered': {'type': 'boolean'}},
                                         'required': ['Metered'],
                                         'type': 'object'}},
     'properties': {'CharmInfo': {'properties': {'Params': {'$ref': '#/definitions/CharmInfo'},
                                                 'Result': {'$ref': '#/definitions/CharmInfo'}},
                                  'type': 'object'},
                    'IsMetered': {'properties': {'Params': {'$ref': '#/definitions/CharmInfo'},
                                                 'Result': {'$ref': '#/definitions/IsMeteredResult'}},
                                  'type': 'object'},
                    'List': {'properties': {'Params': {'$ref': '#/definitions/CharmsList'},
                                            'Result': {'$ref': '#/definitions/CharmsListResult'}},
                             'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(CharmInfo)
    async def CharmInfo(self, charmurl):
        '''
        charmurl : str
        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Charms', Request='CharmInfo', Version=2, Params=params)
        params['CharmURL'] = charmurl
        reply = await self.rpc(msg)
        return self._map(reply, CharmInfo)



    #@ReturnMapping(IsMeteredResult)
    async def IsMetered(self, charmurl):
        '''
        charmurl : str
        Returns -> bool
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Charms', Request='IsMetered', Version=2, Params=params)
        params['CharmURL'] = charmurl
        reply = await self.rpc(msg)
        return self._map(reply, IsMetered)



    #@ReturnMapping(CharmsListResult)
    async def List(self, names):
        '''
        names : typing.Sequence[str]
        Returns -> typing.Sequence[str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Charms', Request='List', Version=2, Params=params)
        params['Names'] = names
        reply = await self.rpc(msg)
        return self._map(reply, List)


class Cleaner(Type):
    name = 'Cleaner'
    version = 2
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Cleanup': {'type': 'object'},
                    'WatchCleanups': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                      'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(None)
    async def Cleanup(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Cleaner', Request='Cleanup', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Cleanup)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchCleanups(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Cleaner', Request='WatchCleanups', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchCleanups)


class Client(Type):
    name = 'Client'
    version = 1
    schema =     {'definitions': {'APIHostPortsResult': {'additionalProperties': False,
                                            'properties': {'Servers': {'items': {'items': {'$ref': '#/definitions/HostPort'},
                                                                                 'type': 'array'},
                                                                       'type': 'array'}},
                                            'required': ['Servers'],
                                            'type': 'object'},
                     'AddCharm': {'additionalProperties': False,
                                  'properties': {'Channel': {'type': 'string'},
                                                 'URL': {'type': 'string'}},
                                  'required': ['URL', 'Channel'],
                                  'type': 'object'},
                     'AddCharmWithAuthorization': {'additionalProperties': False,
                                                   'properties': {'Channel': {'type': 'string'},
                                                                  'CharmStoreMacaroon': {'$ref': '#/definitions/Macaroon'},
                                                                  'URL': {'type': 'string'}},
                                                   'required': ['URL',
                                                                'Channel',
                                                                'CharmStoreMacaroon'],
                                                   'type': 'object'},
                     'AddMachineParams': {'additionalProperties': False,
                                          'properties': {'Addrs': {'items': {'$ref': '#/definitions/Address'},
                                                                   'type': 'array'},
                                                         'Constraints': {'$ref': '#/definitions/Value'},
                                                         'ContainerType': {'type': 'string'},
                                                         'Disks': {'items': {'$ref': '#/definitions/Constraints'},
                                                                   'type': 'array'},
                                                         'HardwareCharacteristics': {'$ref': '#/definitions/HardwareCharacteristics'},
                                                         'InstanceId': {'type': 'string'},
                                                         'Jobs': {'items': {'type': 'string'},
                                                                  'type': 'array'},
                                                         'Nonce': {'type': 'string'},
                                                         'ParentId': {'type': 'string'},
                                                         'Placement': {'$ref': '#/definitions/Placement'},
                                                         'Series': {'type': 'string'}},
                                          'required': ['Series',
                                                       'Constraints',
                                                       'Jobs',
                                                       'Disks',
                                                       'Placement',
                                                       'ParentId',
                                                       'ContainerType',
                                                       'InstanceId',
                                                       'Nonce',
                                                       'HardwareCharacteristics',
                                                       'Addrs'],
                                          'type': 'object'},
                     'AddMachines': {'additionalProperties': False,
                                     'properties': {'MachineParams': {'items': {'$ref': '#/definitions/AddMachineParams'},
                                                                      'type': 'array'}},
                                     'required': ['MachineParams'],
                                     'type': 'object'},
                     'AddMachinesResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'Machine': {'type': 'string'}},
                                           'required': ['Machine', 'Error'],
                                           'type': 'object'},
                     'AddMachinesResults': {'additionalProperties': False,
                                            'properties': {'Machines': {'items': {'$ref': '#/definitions/AddMachinesResult'},
                                                                        'type': 'array'}},
                                            'required': ['Machines'],
                                            'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'AgentVersionResult': {'additionalProperties': False,
                                            'properties': {'Version': {'$ref': '#/definitions/Number'}},
                                            'required': ['Version'],
                                            'type': 'object'},
                     'AllWatcherId': {'additionalProperties': False,
                                      'properties': {'AllWatcherId': {'type': 'string'}},
                                      'required': ['AllWatcherId'],
                                      'type': 'object'},
                     'Binary': {'additionalProperties': False,
                                'properties': {'Arch': {'type': 'string'},
                                               'Number': {'$ref': '#/definitions/Number'},
                                               'Series': {'type': 'string'}},
                                'required': ['Number', 'Series', 'Arch'],
                                'type': 'object'},
                     'BundleChangesChange': {'additionalProperties': False,
                                             'properties': {'args': {'items': {'additionalProperties': True,
                                                                               'type': 'object'},
                                                                     'type': 'array'},
                                                            'id': {'type': 'string'},
                                                            'method': {'type': 'string'},
                                                            'requires': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                             'required': ['id',
                                                          'method',
                                                          'args',
                                                          'requires'],
                                             'type': 'object'},
                     'CharmInfo': {'additionalProperties': False,
                                   'properties': {'CharmURL': {'type': 'string'}},
                                   'required': ['CharmURL'],
                                   'type': 'object'},
                     'Constraints': {'additionalProperties': False,
                                     'properties': {'Count': {'type': 'integer'},
                                                    'Pool': {'type': 'string'},
                                                    'Size': {'type': 'integer'}},
                                     'required': ['Pool', 'Size', 'Count'],
                                     'type': 'object'},
                     'DestroyMachines': {'additionalProperties': False,
                                         'properties': {'Force': {'type': 'boolean'},
                                                        'MachineNames': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                         'required': ['MachineNames', 'Force'],
                                         'type': 'object'},
                     'DetailedStatus': {'additionalProperties': False,
                                        'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                             'type': 'object'}},
                                                                'type': 'object'},
                                                       'Err': {'additionalProperties': True,
                                                               'type': 'object'},
                                                       'Info': {'type': 'string'},
                                                       'Kind': {'type': 'string'},
                                                       'Life': {'type': 'string'},
                                                       'Since': {'format': 'date-time',
                                                                 'type': 'string'},
                                                       'Status': {'type': 'string'},
                                                       'Version': {'type': 'string'}},
                                        'required': ['Status',
                                                     'Info',
                                                     'Data',
                                                     'Since',
                                                     'Kind',
                                                     'Version',
                                                     'Life',
                                                     'Err'],
                                        'type': 'object'},
                     'EndpointStatus': {'additionalProperties': False,
                                        'properties': {'Name': {'type': 'string'},
                                                       'Role': {'type': 'string'},
                                                       'ServiceName': {'type': 'string'},
                                                       'Subordinate': {'type': 'boolean'}},
                                        'required': ['ServiceName',
                                                     'Name',
                                                     'Role',
                                                     'Subordinate'],
                                        'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatus': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Info': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'FindToolsParams': {'additionalProperties': False,
                                         'properties': {'Arch': {'type': 'string'},
                                                        'MajorVersion': {'type': 'integer'},
                                                        'MinorVersion': {'type': 'integer'},
                                                        'Number': {'$ref': '#/definitions/Number'},
                                                        'Series': {'type': 'string'}},
                                         'required': ['Number',
                                                      'MajorVersion',
                                                      'MinorVersion',
                                                      'Arch',
                                                      'Series'],
                                         'type': 'object'},
                     'FindToolsResult': {'additionalProperties': False,
                                         'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                        'List': {'items': {'$ref': '#/definitions/Tools'},
                                                                 'type': 'array'}},
                                         'required': ['List', 'Error'],
                                         'type': 'object'},
                     'FullStatus': {'additionalProperties': False,
                                    'properties': {'AvailableVersion': {'type': 'string'},
                                                   'Machines': {'patternProperties': {'.*': {'$ref': '#/definitions/MachineStatus'}},
                                                                'type': 'object'},
                                                   'ModelName': {'type': 'string'},
                                                   'Relations': {'items': {'$ref': '#/definitions/RelationStatus'},
                                                                 'type': 'array'},
                                                   'Services': {'patternProperties': {'.*': {'$ref': '#/definitions/ServiceStatus'}},
                                                                'type': 'object'}},
                                    'required': ['ModelName',
                                                 'AvailableVersion',
                                                 'Machines',
                                                 'Services',
                                                 'Relations'],
                                    'type': 'object'},
                     'GetBundleChangesParams': {'additionalProperties': False,
                                                'properties': {'yaml': {'type': 'string'}},
                                                'required': ['yaml'],
                                                'type': 'object'},
                     'GetBundleChangesResults': {'additionalProperties': False,
                                                 'properties': {'changes': {'items': {'$ref': '#/definitions/BundleChangesChange'},
                                                                            'type': 'array'},
                                                                'errors': {'items': {'type': 'string'},
                                                                           'type': 'array'}},
                                                 'type': 'object'},
                     'GetConstraintsResults': {'additionalProperties': False,
                                               'properties': {'Constraints': {'$ref': '#/definitions/Value'}},
                                               'required': ['Constraints'],
                                               'type': 'object'},
                     'HardwareCharacteristics': {'additionalProperties': False,
                                                 'properties': {'Arch': {'type': 'string'},
                                                                'AvailabilityZone': {'type': 'string'},
                                                                'CpuCores': {'type': 'integer'},
                                                                'CpuPower': {'type': 'integer'},
                                                                'Mem': {'type': 'integer'},
                                                                'RootDisk': {'type': 'integer'},
                                                                'Tags': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                                 'type': 'object'},
                     'HostPort': {'additionalProperties': False,
                                  'properties': {'Address': {'$ref': '#/definitions/Address'},
                                                 'Port': {'type': 'integer'}},
                                  'required': ['Address', 'Port'],
                                  'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineStatus': {'additionalProperties': False,
                                       'properties': {'AgentStatus': {'$ref': '#/definitions/DetailedStatus'},
                                                      'Containers': {'patternProperties': {'.*': {'$ref': '#/definitions/MachineStatus'}},
                                                                     'type': 'object'},
                                                      'DNSName': {'type': 'string'},
                                                      'Hardware': {'type': 'string'},
                                                      'HasVote': {'type': 'boolean'},
                                                      'Id': {'type': 'string'},
                                                      'InstanceId': {'type': 'string'},
                                                      'InstanceStatus': {'$ref': '#/definitions/DetailedStatus'},
                                                      'Jobs': {'items': {'type': 'string'},
                                                               'type': 'array'},
                                                      'Series': {'type': 'string'},
                                                      'WantsVote': {'type': 'boolean'}},
                                       'required': ['AgentStatus',
                                                    'InstanceStatus',
                                                    'DNSName',
                                                    'InstanceId',
                                                    'Series',
                                                    'Id',
                                                    'Containers',
                                                    'Hardware',
                                                    'Jobs',
                                                    'HasVote',
                                                    'WantsVote'],
                                       'type': 'object'},
                     'MeterStatus': {'additionalProperties': False,
                                     'properties': {'Color': {'type': 'string'},
                                                    'Message': {'type': 'string'}},
                                     'required': ['Color', 'Message'],
                                     'type': 'object'},
                     'ModelConfigResults': {'additionalProperties': False,
                                            'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                   'type': 'object'}},
                                                                      'type': 'object'}},
                                            'required': ['Config'],
                                            'type': 'object'},
                     'ModelInfo': {'additionalProperties': False,
                                   'properties': {'DefaultSeries': {'type': 'string'},
                                                  'Life': {'type': 'string'},
                                                  'Name': {'type': 'string'},
                                                  'OwnerTag': {'type': 'string'},
                                                  'ProviderType': {'type': 'string'},
                                                  'ServerUUID': {'type': 'string'},
                                                  'Status': {'$ref': '#/definitions/EntityStatus'},
                                                  'UUID': {'type': 'string'},
                                                  'Users': {'items': {'$ref': '#/definitions/ModelUserInfo'},
                                                            'type': 'array'}},
                                   'required': ['Name',
                                                'UUID',
                                                'ServerUUID',
                                                'ProviderType',
                                                'DefaultSeries',
                                                'OwnerTag',
                                                'Life',
                                                'Status',
                                                'Users'],
                                   'type': 'object'},
                     'ModelSet': {'additionalProperties': False,
                                  'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                         'type': 'object'}},
                                                            'type': 'object'}},
                                  'required': ['Config'],
                                  'type': 'object'},
                     'ModelUnset': {'additionalProperties': False,
                                    'properties': {'Keys': {'items': {'type': 'string'},
                                                            'type': 'array'}},
                                    'required': ['Keys'],
                                    'type': 'object'},
                     'ModelUserInfo': {'additionalProperties': False,
                                       'properties': {'access': {'type': 'string'},
                                                      'displayname': {'type': 'string'},
                                                      'lastconnection': {'format': 'date-time',
                                                                         'type': 'string'},
                                                      'user': {'type': 'string'}},
                                       'required': ['user',
                                                    'displayname',
                                                    'lastconnection',
                                                    'access'],
                                       'type': 'object'},
                     'ModelUserInfoResult': {'additionalProperties': False,
                                             'properties': {'error': {'$ref': '#/definitions/Error'},
                                                            'result': {'$ref': '#/definitions/ModelUserInfo'}},
                                             'type': 'object'},
                     'ModelUserInfoResults': {'additionalProperties': False,
                                              'properties': {'results': {'items': {'$ref': '#/definitions/ModelUserInfoResult'},
                                                                         'type': 'array'}},
                                              'required': ['results'],
                                              'type': 'object'},
                     'Number': {'additionalProperties': False,
                                'properties': {'Build': {'type': 'integer'},
                                               'Major': {'type': 'integer'},
                                               'Minor': {'type': 'integer'},
                                               'Patch': {'type': 'integer'},
                                               'Tag': {'type': 'string'}},
                                'required': ['Major',
                                             'Minor',
                                             'Tag',
                                             'Patch',
                                             'Build'],
                                'type': 'object'},
                     'Placement': {'additionalProperties': False,
                                   'properties': {'Directive': {'type': 'string'},
                                                  'Scope': {'type': 'string'}},
                                   'required': ['Scope', 'Directive'],
                                   'type': 'object'},
                     'PrivateAddress': {'additionalProperties': False,
                                        'properties': {'Target': {'type': 'string'}},
                                        'required': ['Target'],
                                        'type': 'object'},
                     'PrivateAddressResults': {'additionalProperties': False,
                                               'properties': {'PrivateAddress': {'type': 'string'}},
                                               'required': ['PrivateAddress'],
                                               'type': 'object'},
                     'ProvisioningScriptParams': {'additionalProperties': False,
                                                  'properties': {'DataDir': {'type': 'string'},
                                                                 'DisablePackageCommands': {'type': 'boolean'},
                                                                 'MachineId': {'type': 'string'},
                                                                 'Nonce': {'type': 'string'}},
                                                  'required': ['MachineId',
                                                               'Nonce',
                                                               'DataDir',
                                                               'DisablePackageCommands'],
                                                  'type': 'object'},
                     'ProvisioningScriptResult': {'additionalProperties': False,
                                                  'properties': {'Script': {'type': 'string'}},
                                                  'required': ['Script'],
                                                  'type': 'object'},
                     'PublicAddress': {'additionalProperties': False,
                                       'properties': {'Target': {'type': 'string'}},
                                       'required': ['Target'],
                                       'type': 'object'},
                     'PublicAddressResults': {'additionalProperties': False,
                                              'properties': {'PublicAddress': {'type': 'string'}},
                                              'required': ['PublicAddress'],
                                              'type': 'object'},
                     'RelationStatus': {'additionalProperties': False,
                                        'properties': {'Endpoints': {'items': {'$ref': '#/definitions/EndpointStatus'},
                                                                     'type': 'array'},
                                                       'Id': {'type': 'integer'},
                                                       'Interface': {'type': 'string'},
                                                       'Key': {'type': 'string'},
                                                       'Scope': {'type': 'string'}},
                                        'required': ['Id',
                                                     'Key',
                                                     'Interface',
                                                     'Scope',
                                                     'Endpoints'],
                                        'type': 'object'},
                     'ResolveCharmResult': {'additionalProperties': False,
                                            'properties': {'Error': {'type': 'string'},
                                                           'URL': {'$ref': '#/definitions/URL'}},
                                            'type': 'object'},
                     'ResolveCharmResults': {'additionalProperties': False,
                                             'properties': {'URLs': {'items': {'$ref': '#/definitions/ResolveCharmResult'},
                                                                     'type': 'array'}},
                                             'required': ['URLs'],
                                             'type': 'object'},
                     'ResolveCharms': {'additionalProperties': False,
                                       'properties': {'References': {'items': {'$ref': '#/definitions/URL'},
                                                                     'type': 'array'}},
                                       'required': ['References'],
                                       'type': 'object'},
                     'Resolved': {'additionalProperties': False,
                                  'properties': {'Retry': {'type': 'boolean'},
                                                 'UnitName': {'type': 'string'}},
                                  'required': ['UnitName', 'Retry'],
                                  'type': 'object'},
                     'ServiceStatus': {'additionalProperties': False,
                                       'properties': {'CanUpgradeTo': {'type': 'string'},
                                                      'Charm': {'type': 'string'},
                                                      'Err': {'additionalProperties': True,
                                                              'type': 'object'},
                                                      'Exposed': {'type': 'boolean'},
                                                      'Life': {'type': 'string'},
                                                      'MeterStatuses': {'patternProperties': {'.*': {'$ref': '#/definitions/MeterStatus'}},
                                                                        'type': 'object'},
                                                      'Relations': {'patternProperties': {'.*': {'items': {'type': 'string'},
                                                                                                 'type': 'array'}},
                                                                    'type': 'object'},
                                                      'Status': {'$ref': '#/definitions/DetailedStatus'},
                                                      'SubordinateTo': {'items': {'type': 'string'},
                                                                        'type': 'array'},
                                                      'Units': {'patternProperties': {'.*': {'$ref': '#/definitions/UnitStatus'}},
                                                                'type': 'object'}},
                                       'required': ['Err',
                                                    'Charm',
                                                    'Exposed',
                                                    'Life',
                                                    'Relations',
                                                    'CanUpgradeTo',
                                                    'SubordinateTo',
                                                    'Units',
                                                    'MeterStatuses',
                                                    'Status'],
                                       'type': 'object'},
                     'SetConstraints': {'additionalProperties': False,
                                        'properties': {'Constraints': {'$ref': '#/definitions/Value'},
                                                       'ServiceName': {'type': 'string'}},
                                        'required': ['ServiceName', 'Constraints'],
                                        'type': 'object'},
                     'SetModelAgentVersion': {'additionalProperties': False,
                                              'properties': {'Version': {'$ref': '#/definitions/Number'}},
                                              'required': ['Version'],
                                              'type': 'object'},
                     'StatusHistoryArgs': {'additionalProperties': False,
                                           'properties': {'Kind': {'type': 'string'},
                                                          'Name': {'type': 'string'},
                                                          'Size': {'type': 'integer'}},
                                           'required': ['Kind', 'Size', 'Name'],
                                           'type': 'object'},
                     'StatusHistoryResults': {'additionalProperties': False,
                                              'properties': {'Statuses': {'items': {'$ref': '#/definitions/DetailedStatus'},
                                                                          'type': 'array'}},
                                              'required': ['Statuses'],
                                              'type': 'object'},
                     'StatusParams': {'additionalProperties': False,
                                      'properties': {'Patterns': {'items': {'type': 'string'},
                                                                  'type': 'array'}},
                                      'required': ['Patterns'],
                                      'type': 'object'},
                     'Tools': {'additionalProperties': False,
                               'properties': {'sha256': {'type': 'string'},
                                              'size': {'type': 'integer'},
                                              'url': {'type': 'string'},
                                              'version': {'$ref': '#/definitions/Binary'}},
                               'required': ['version', 'url', 'size'],
                               'type': 'object'},
                     'URL': {'additionalProperties': False,
                             'properties': {'Channel': {'type': 'string'},
                                            'Name': {'type': 'string'},
                                            'Revision': {'type': 'integer'},
                                            'Schema': {'type': 'string'},
                                            'Series': {'type': 'string'},
                                            'User': {'type': 'string'}},
                             'required': ['Schema',
                                          'User',
                                          'Name',
                                          'Revision',
                                          'Series',
                                          'Channel'],
                             'type': 'object'},
                     'UnitStatus': {'additionalProperties': False,
                                    'properties': {'AgentStatus': {'$ref': '#/definitions/DetailedStatus'},
                                                   'Charm': {'type': 'string'},
                                                   'Machine': {'type': 'string'},
                                                   'OpenedPorts': {'items': {'type': 'string'},
                                                                   'type': 'array'},
                                                   'PublicAddress': {'type': 'string'},
                                                   'Subordinates': {'patternProperties': {'.*': {'$ref': '#/definitions/UnitStatus'}},
                                                                    'type': 'object'},
                                                   'WorkloadStatus': {'$ref': '#/definitions/DetailedStatus'}},
                                    'required': ['AgentStatus',
                                                 'WorkloadStatus',
                                                 'Machine',
                                                 'OpenedPorts',
                                                 'PublicAddress',
                                                 'Charm',
                                                 'Subordinates'],
                                    'type': 'object'},
                     'Value': {'additionalProperties': False,
                               'properties': {'arch': {'type': 'string'},
                                              'container': {'type': 'string'},
                                              'cpu-cores': {'type': 'integer'},
                                              'cpu-power': {'type': 'integer'},
                                              'instance-type': {'type': 'string'},
                                              'mem': {'type': 'integer'},
                                              'root-disk': {'type': 'integer'},
                                              'spaces': {'items': {'type': 'string'},
                                                         'type': 'array'},
                                              'tags': {'items': {'type': 'string'},
                                                       'type': 'array'},
                                              'virt-type': {'type': 'string'}},
                               'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'APIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/APIHostPortsResult'}},
                                     'type': 'object'},
                    'AbortCurrentUpgrade': {'type': 'object'},
                    'AddCharm': {'properties': {'Params': {'$ref': '#/definitions/AddCharm'}},
                                 'type': 'object'},
                    'AddCharmWithAuthorization': {'properties': {'Params': {'$ref': '#/definitions/AddCharmWithAuthorization'}},
                                                  'type': 'object'},
                    'AddMachines': {'properties': {'Params': {'$ref': '#/definitions/AddMachines'},
                                                   'Result': {'$ref': '#/definitions/AddMachinesResults'}},
                                    'type': 'object'},
                    'AddMachinesV2': {'properties': {'Params': {'$ref': '#/definitions/AddMachines'},
                                                     'Result': {'$ref': '#/definitions/AddMachinesResults'}},
                                      'type': 'object'},
                    'AgentVersion': {'properties': {'Result': {'$ref': '#/definitions/AgentVersionResult'}},
                                     'type': 'object'},
                    'CharmInfo': {'properties': {'Params': {'$ref': '#/definitions/CharmInfo'},
                                                 'Result': {'$ref': '#/definitions/CharmInfo'}},
                                  'type': 'object'},
                    'DestroyMachines': {'properties': {'Params': {'$ref': '#/definitions/DestroyMachines'}},
                                        'type': 'object'},
                    'DestroyModel': {'type': 'object'},
                    'FindTools': {'properties': {'Params': {'$ref': '#/definitions/FindToolsParams'},
                                                 'Result': {'$ref': '#/definitions/FindToolsResult'}},
                                  'type': 'object'},
                    'FullStatus': {'properties': {'Params': {'$ref': '#/definitions/StatusParams'},
                                                  'Result': {'$ref': '#/definitions/FullStatus'}},
                                   'type': 'object'},
                    'GetBundleChanges': {'properties': {'Params': {'$ref': '#/definitions/GetBundleChangesParams'},
                                                        'Result': {'$ref': '#/definitions/GetBundleChangesResults'}},
                                         'type': 'object'},
                    'GetModelConstraints': {'properties': {'Result': {'$ref': '#/definitions/GetConstraintsResults'}},
                                            'type': 'object'},
                    'InjectMachines': {'properties': {'Params': {'$ref': '#/definitions/AddMachines'},
                                                      'Result': {'$ref': '#/definitions/AddMachinesResults'}},
                                       'type': 'object'},
                    'ModelGet': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResults'}},
                                 'type': 'object'},
                    'ModelInfo': {'properties': {'Result': {'$ref': '#/definitions/ModelInfo'}},
                                  'type': 'object'},
                    'ModelSet': {'properties': {'Params': {'$ref': '#/definitions/ModelSet'}},
                                 'type': 'object'},
                    'ModelUnset': {'properties': {'Params': {'$ref': '#/definitions/ModelUnset'}},
                                   'type': 'object'},
                    'ModelUserInfo': {'properties': {'Result': {'$ref': '#/definitions/ModelUserInfoResults'}},
                                      'type': 'object'},
                    'PrivateAddress': {'properties': {'Params': {'$ref': '#/definitions/PrivateAddress'},
                                                      'Result': {'$ref': '#/definitions/PrivateAddressResults'}},
                                       'type': 'object'},
                    'ProvisioningScript': {'properties': {'Params': {'$ref': '#/definitions/ProvisioningScriptParams'},
                                                          'Result': {'$ref': '#/definitions/ProvisioningScriptResult'}},
                                           'type': 'object'},
                    'PublicAddress': {'properties': {'Params': {'$ref': '#/definitions/PublicAddress'},
                                                     'Result': {'$ref': '#/definitions/PublicAddressResults'}},
                                      'type': 'object'},
                    'ResolveCharms': {'properties': {'Params': {'$ref': '#/definitions/ResolveCharms'},
                                                     'Result': {'$ref': '#/definitions/ResolveCharmResults'}},
                                      'type': 'object'},
                    'Resolved': {'properties': {'Params': {'$ref': '#/definitions/Resolved'}},
                                 'type': 'object'},
                    'RetryProvisioning': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'},
                    'SetModelAgentVersion': {'properties': {'Params': {'$ref': '#/definitions/SetModelAgentVersion'}},
                                             'type': 'object'},
                    'SetModelConstraints': {'properties': {'Params': {'$ref': '#/definitions/SetConstraints'}},
                                            'type': 'object'},
                    'StatusHistory': {'properties': {'Params': {'$ref': '#/definitions/StatusHistoryArgs'},
                                                     'Result': {'$ref': '#/definitions/StatusHistoryResults'}},
                                      'type': 'object'},
                    'WatchAll': {'properties': {'Result': {'$ref': '#/definitions/AllWatcherId'}},
                                 'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(APIHostPortsResult)
    async def APIHostPorts(self):
        '''

        Returns -> typing.Sequence[~HostPort]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='APIHostPorts', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIHostPorts)



    #@ReturnMapping(None)
    async def AbortCurrentUpgrade(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AbortCurrentUpgrade', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, AbortCurrentUpgrade)



    #@ReturnMapping(None)
    async def AddCharm(self, channel, url):
        '''
        channel : str
        url : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AddCharm', Version=1, Params=params)
        params['Channel'] = channel
        params['URL'] = url
        reply = await self.rpc(msg)
        return self._map(reply, AddCharm)



    #@ReturnMapping(None)
    async def AddCharmWithAuthorization(self, charmstoremacaroon, channel, url):
        '''
        charmstoremacaroon : ~Macaroon
        channel : str
        url : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AddCharmWithAuthorization', Version=1, Params=params)
        params['CharmStoreMacaroon'] = charmstoremacaroon
        params['Channel'] = channel
        params['URL'] = url
        reply = await self.rpc(msg)
        return self._map(reply, AddCharmWithAuthorization)



    #@ReturnMapping(AddMachinesResults)
    async def AddMachines(self, machineparams):
        '''
        machineparams : typing.Sequence[~AddMachineParams]
        Returns -> typing.Sequence[~AddMachinesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AddMachines', Version=1, Params=params)
        params['MachineParams'] = machineparams
        reply = await self.rpc(msg)
        return self._map(reply, AddMachines)



    #@ReturnMapping(AddMachinesResults)
    async def AddMachinesV2(self, machineparams):
        '''
        machineparams : typing.Sequence[~AddMachineParams]
        Returns -> typing.Sequence[~AddMachinesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AddMachinesV2', Version=1, Params=params)
        params['MachineParams'] = machineparams
        reply = await self.rpc(msg)
        return self._map(reply, AddMachinesV2)



    #@ReturnMapping(AgentVersionResult)
    async def AgentVersion(self):
        '''

        Returns -> ~Number
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='AgentVersion', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, AgentVersion)



    #@ReturnMapping(CharmInfo)
    async def CharmInfo(self, charmurl):
        '''
        charmurl : str
        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='CharmInfo', Version=1, Params=params)
        params['CharmURL'] = charmurl
        reply = await self.rpc(msg)
        return self._map(reply, CharmInfo)



    #@ReturnMapping(None)
    async def DestroyMachines(self, machinenames, force):
        '''
        machinenames : typing.Sequence[str]
        force : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='DestroyMachines', Version=1, Params=params)
        params['MachineNames'] = machinenames
        params['Force'] = force
        reply = await self.rpc(msg)
        return self._map(reply, DestroyMachines)



    #@ReturnMapping(None)
    async def DestroyModel(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='DestroyModel', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, DestroyModel)



    #@ReturnMapping(FindToolsResult)
    async def FindTools(self, majorversion, series, minorversion, arch, number):
        '''
        majorversion : int
        series : str
        minorversion : int
        arch : str
        number : ~Number
        Returns -> typing.Union[~Error, typing.Sequence[~Tools]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='FindTools', Version=1, Params=params)
        params['MajorVersion'] = majorversion
        params['Series'] = series
        params['MinorVersion'] = minorversion
        params['Arch'] = arch
        params['Number'] = number
        reply = await self.rpc(msg)
        return self._map(reply, FindTools)



    #@ReturnMapping(FullStatus)
    async def FullStatus(self, patterns):
        '''
        patterns : typing.Sequence[str]
        Returns -> typing.Union[typing.Mapping[str, ~MachineStatus], typing.Sequence[~RelationStatus]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='FullStatus', Version=1, Params=params)
        params['Patterns'] = patterns
        reply = await self.rpc(msg)
        return self._map(reply, FullStatus)



    #@ReturnMapping(GetBundleChangesResults)
    async def GetBundleChanges(self, yaml):
        '''
        yaml : str
        Returns -> typing.Sequence[~BundleChangesChange]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='GetBundleChanges', Version=1, Params=params)
        params['yaml'] = yaml
        reply = await self.rpc(msg)
        return self._map(reply, GetBundleChanges)



    #@ReturnMapping(GetConstraintsResults)
    async def GetModelConstraints(self):
        '''

        Returns -> ~Value
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='GetModelConstraints', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, GetModelConstraints)



    #@ReturnMapping(AddMachinesResults)
    async def InjectMachines(self, machineparams):
        '''
        machineparams : typing.Sequence[~AddMachineParams]
        Returns -> typing.Sequence[~AddMachinesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='InjectMachines', Version=1, Params=params)
        params['MachineParams'] = machineparams
        reply = await self.rpc(msg)
        return self._map(reply, InjectMachines)



    #@ReturnMapping(ModelConfigResults)
    async def ModelGet(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ModelGet', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelGet)



    #@ReturnMapping(ModelInfo)
    async def ModelInfo(self):
        '''

        Returns -> typing.Union[typing.Sequence[~ModelUserInfo], ~EntityStatus]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ModelInfo', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelInfo)



    #@ReturnMapping(None)
    async def ModelSet(self, config):
        '''
        config : typing.Mapping[str, typing.Any]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ModelSet', Version=1, Params=params)
        params['Config'] = config
        reply = await self.rpc(msg)
        return self._map(reply, ModelSet)



    #@ReturnMapping(None)
    async def ModelUnset(self, keys):
        '''
        keys : typing.Sequence[str]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ModelUnset', Version=1, Params=params)
        params['Keys'] = keys
        reply = await self.rpc(msg)
        return self._map(reply, ModelUnset)



    #@ReturnMapping(ModelUserInfoResults)
    async def ModelUserInfo(self):
        '''

        Returns -> typing.Sequence[~ModelUserInfoResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ModelUserInfo', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelUserInfo)



    #@ReturnMapping(PrivateAddressResults)
    async def PrivateAddress(self, target):
        '''
        target : str
        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='PrivateAddress', Version=1, Params=params)
        params['Target'] = target
        reply = await self.rpc(msg)
        return self._map(reply, PrivateAddress)



    #@ReturnMapping(ProvisioningScriptResult)
    async def ProvisioningScript(self, datadir, disablepackagecommands, nonce, machineid):
        '''
        datadir : str
        disablepackagecommands : bool
        nonce : str
        machineid : str
        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ProvisioningScript', Version=1, Params=params)
        params['DataDir'] = datadir
        params['DisablePackageCommands'] = disablepackagecommands
        params['Nonce'] = nonce
        params['MachineId'] = machineid
        reply = await self.rpc(msg)
        return self._map(reply, ProvisioningScript)



    #@ReturnMapping(PublicAddressResults)
    async def PublicAddress(self, target):
        '''
        target : str
        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='PublicAddress', Version=1, Params=params)
        params['Target'] = target
        reply = await self.rpc(msg)
        return self._map(reply, PublicAddress)



    #@ReturnMapping(ResolveCharmResults)
    async def ResolveCharms(self, references):
        '''
        references : typing.Sequence[~URL]
        Returns -> typing.Sequence[~ResolveCharmResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='ResolveCharms', Version=1, Params=params)
        params['References'] = references
        reply = await self.rpc(msg)
        return self._map(reply, ResolveCharms)



    #@ReturnMapping(None)
    async def Resolved(self, unitname, retry):
        '''
        unitname : str
        retry : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='Resolved', Version=1, Params=params)
        params['UnitName'] = unitname
        params['Retry'] = retry
        reply = await self.rpc(msg)
        return self._map(reply, Resolved)



    #@ReturnMapping(ErrorResults)
    async def RetryProvisioning(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='RetryProvisioning', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, RetryProvisioning)



    #@ReturnMapping(None)
    async def SetModelAgentVersion(self, build, minor, tag, patch, major):
        '''
        build : int
        minor : int
        tag : str
        patch : int
        major : int
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='SetModelAgentVersion', Version=1, Params=params)
        params['Build'] = build
        params['Minor'] = minor
        params['Tag'] = tag
        params['Patch'] = patch
        params['Major'] = major
        reply = await self.rpc(msg)
        return self._map(reply, SetModelAgentVersion)



    #@ReturnMapping(None)
    async def SetModelConstraints(self, constraints, servicename):
        '''
        constraints : ~Value
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='SetModelConstraints', Version=1, Params=params)
        params['Constraints'] = constraints
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, SetModelConstraints)



    #@ReturnMapping(StatusHistoryResults)
    async def StatusHistory(self, name, kind, size):
        '''
        name : str
        kind : str
        size : int
        Returns -> typing.Sequence[~DetailedStatus]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='StatusHistory', Version=1, Params=params)
        params['Name'] = name
        params['Kind'] = kind
        params['Size'] = size
        reply = await self.rpc(msg)
        return self._map(reply, StatusHistory)



    #@ReturnMapping(AllWatcherId)
    async def WatchAll(self):
        '''

        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Client', Request='WatchAll', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAll)


class Controller(Type):
    name = 'Controller'
    version = 2
    schema =     {'definitions': {'AllWatcherId': {'additionalProperties': False,
                                      'properties': {'AllWatcherId': {'type': 'string'}},
                                      'required': ['AllWatcherId'],
                                      'type': 'object'},
                     'DestroyControllerArgs': {'additionalProperties': False,
                                               'properties': {'destroy-models': {'type': 'boolean'}},
                                               'required': ['destroy-models'],
                                               'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'InitiateModelMigrationArgs': {'additionalProperties': False,
                                                    'properties': {'specs': {'items': {'$ref': '#/definitions/ModelMigrationSpec'},
                                                                             'type': 'array'}},
                                                    'required': ['specs'],
                                                    'type': 'object'},
                     'InitiateModelMigrationResult': {'additionalProperties': False,
                                                      'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                     'id': {'type': 'string'},
                                                                     'model-tag': {'type': 'string'}},
                                                      'required': ['model-tag',
                                                                   'error',
                                                                   'id'],
                                                      'type': 'object'},
                     'InitiateModelMigrationResults': {'additionalProperties': False,
                                                       'properties': {'results': {'items': {'$ref': '#/definitions/InitiateModelMigrationResult'},
                                                                                  'type': 'array'}},
                                                       'required': ['results'],
                                                       'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Model': {'additionalProperties': False,
                               'properties': {'Name': {'type': 'string'},
                                              'OwnerTag': {'type': 'string'},
                                              'UUID': {'type': 'string'}},
                               'required': ['Name', 'UUID', 'OwnerTag'],
                               'type': 'object'},
                     'ModelBlockInfo': {'additionalProperties': False,
                                        'properties': {'blocks': {'items': {'type': 'string'},
                                                                  'type': 'array'},
                                                       'model-uuid': {'type': 'string'},
                                                       'name': {'type': 'string'},
                                                       'owner-tag': {'type': 'string'}},
                                        'required': ['name',
                                                     'model-uuid',
                                                     'owner-tag',
                                                     'blocks'],
                                        'type': 'object'},
                     'ModelBlockInfoList': {'additionalProperties': False,
                                            'properties': {'models': {'items': {'$ref': '#/definitions/ModelBlockInfo'},
                                                                      'type': 'array'}},
                                            'type': 'object'},
                     'ModelConfigResults': {'additionalProperties': False,
                                            'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                   'type': 'object'}},
                                                                      'type': 'object'}},
                                            'required': ['Config'],
                                            'type': 'object'},
                     'ModelMigrationSpec': {'additionalProperties': False,
                                            'properties': {'model-tag': {'type': 'string'},
                                                           'target-info': {'$ref': '#/definitions/ModelMigrationTargetInfo'}},
                                            'required': ['model-tag',
                                                         'target-info'],
                                            'type': 'object'},
                     'ModelMigrationTargetInfo': {'additionalProperties': False,
                                                  'properties': {'addrs': {'items': {'type': 'string'},
                                                                           'type': 'array'},
                                                                 'auth-tag': {'type': 'string'},
                                                                 'ca-cert': {'type': 'string'},
                                                                 'controller-tag': {'type': 'string'},
                                                                 'password': {'type': 'string'}},
                                                  'required': ['controller-tag',
                                                               'addrs',
                                                               'ca-cert',
                                                               'auth-tag',
                                                               'password'],
                                                  'type': 'object'},
                     'ModelStatus': {'additionalProperties': False,
                                     'properties': {'hosted-machine-count': {'type': 'integer'},
                                                    'life': {'type': 'string'},
                                                    'model-tag': {'type': 'string'},
                                                    'owner-tag': {'type': 'string'},
                                                    'service-count': {'type': 'integer'}},
                                     'required': ['model-tag',
                                                  'life',
                                                  'hosted-machine-count',
                                                  'service-count',
                                                  'owner-tag'],
                                     'type': 'object'},
                     'ModelStatusResults': {'additionalProperties': False,
                                            'properties': {'models': {'items': {'$ref': '#/definitions/ModelStatus'},
                                                                      'type': 'array'}},
                                            'required': ['models'],
                                            'type': 'object'},
                     'RemoveBlocksArgs': {'additionalProperties': False,
                                          'properties': {'all': {'type': 'boolean'}},
                                          'required': ['all'],
                                          'type': 'object'},
                     'UserModel': {'additionalProperties': False,
                                   'properties': {'LastConnection': {'format': 'date-time',
                                                                     'type': 'string'},
                                                  'Model': {'$ref': '#/definitions/Model'}},
                                   'required': ['Model', 'LastConnection'],
                                   'type': 'object'},
                     'UserModelList': {'additionalProperties': False,
                                       'properties': {'UserModels': {'items': {'$ref': '#/definitions/UserModel'},
                                                                     'type': 'array'}},
                                       'required': ['UserModels'],
                                       'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AllModels': {'properties': {'Result': {'$ref': '#/definitions/UserModelList'}},
                                  'type': 'object'},
                    'DestroyController': {'properties': {'Params': {'$ref': '#/definitions/DestroyControllerArgs'}},
                                          'type': 'object'},
                    'InitiateModelMigration': {'properties': {'Params': {'$ref': '#/definitions/InitiateModelMigrationArgs'},
                                                              'Result': {'$ref': '#/definitions/InitiateModelMigrationResults'}},
                                               'type': 'object'},
                    'ListBlockedModels': {'properties': {'Result': {'$ref': '#/definitions/ModelBlockInfoList'}},
                                          'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResults'}},
                                    'type': 'object'},
                    'ModelStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ModelStatusResults'}},
                                    'type': 'object'},
                    'RemoveBlocks': {'properties': {'Params': {'$ref': '#/definitions/RemoveBlocksArgs'}},
                                     'type': 'object'},
                    'WatchAllModels': {'properties': {'Result': {'$ref': '#/definitions/AllWatcherId'}},
                                       'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(UserModelList)
    async def AllModels(self):
        '''

        Returns -> typing.Sequence[~UserModel]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='AllModels', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, AllModels)



    #@ReturnMapping(None)
    async def DestroyController(self, destroy_models):
        '''
        destroy_models : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='DestroyController', Version=2, Params=params)
        params['destroy-models'] = destroy_models
        reply = await self.rpc(msg)
        return self._map(reply, DestroyController)



    #@ReturnMapping(InitiateModelMigrationResults)
    async def InitiateModelMigration(self, specs):
        '''
        specs : typing.Sequence[~ModelMigrationSpec]
        Returns -> typing.Sequence[~InitiateModelMigrationResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='InitiateModelMigration', Version=2, Params=params)
        params['specs'] = specs
        reply = await self.rpc(msg)
        return self._map(reply, InitiateModelMigration)



    #@ReturnMapping(ModelBlockInfoList)
    async def ListBlockedModels(self):
        '''

        Returns -> typing.Sequence[~ModelBlockInfo]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='ListBlockedModels', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ListBlockedModels)



    #@ReturnMapping(ModelConfigResults)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(ModelStatusResults)
    async def ModelStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ModelStatus]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='ModelStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ModelStatus)



    #@ReturnMapping(None)
    async def RemoveBlocks(self, all_):
        '''
        all_ : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='RemoveBlocks', Version=2, Params=params)
        params['all'] = all_
        reply = await self.rpc(msg)
        return self._map(reply, RemoveBlocks)



    #@ReturnMapping(AllWatcherId)
    async def WatchAllModels(self):
        '''

        Returns -> str
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Controller', Request='WatchAllModels', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAllModels)


class Deployer(Type):
    name = 'Deployer'
    version = 1
    schema =     {'definitions': {'APIHostPortsResult': {'additionalProperties': False,
                                            'properties': {'Servers': {'items': {'items': {'$ref': '#/definitions/HostPort'},
                                                                                 'type': 'array'},
                                                                       'type': 'array'}},
                                            'required': ['Servers'],
                                            'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'BytesResult': {'additionalProperties': False,
                                     'properties': {'Result': {'items': {'type': 'integer'},
                                                               'type': 'array'}},
                                     'required': ['Result'],
                                     'type': 'object'},
                     'DeployerConnectionValues': {'additionalProperties': False,
                                                  'properties': {'APIAddresses': {'items': {'type': 'string'},
                                                                                  'type': 'array'},
                                                                 'StateAddresses': {'items': {'type': 'string'},
                                                                                    'type': 'array'}},
                                                  'required': ['StateAddresses',
                                                               'APIAddresses'],
                                                  'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityPassword': {'additionalProperties': False,
                                        'properties': {'Password': {'type': 'string'},
                                                       'Tag': {'type': 'string'}},
                                        'required': ['Tag', 'Password'],
                                        'type': 'object'},
                     'EntityPasswords': {'additionalProperties': False,
                                         'properties': {'Changes': {'items': {'$ref': '#/definitions/EntityPassword'},
                                                                    'type': 'array'}},
                                         'required': ['Changes'],
                                         'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'HostPort': {'additionalProperties': False,
                                  'properties': {'Address': {'$ref': '#/definitions/Address'},
                                                 'Port': {'type': 'integer'}},
                                  'required': ['Address', 'Port'],
                                  'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'APIAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                     'type': 'object'},
                    'APIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/APIHostPortsResult'}},
                                     'type': 'object'},
                    'CACert': {'properties': {'Result': {'$ref': '#/definitions/BytesResult'}},
                               'type': 'object'},
                    'ConnectionInfo': {'properties': {'Result': {'$ref': '#/definitions/DeployerConnectionValues'}},
                                       'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'ModelUUID': {'properties': {'Result': {'$ref': '#/definitions/StringResult'}},
                                  'type': 'object'},
                    'Remove': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                               'type': 'object'},
                    'SetPasswords': {'properties': {'Params': {'$ref': '#/definitions/EntityPasswords'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'StateAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                       'type': 'object'},
                    'WatchAPIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                          'type': 'object'},
                    'WatchUnits': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsResult)
    async def APIAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='APIAddresses', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIAddresses)



    #@ReturnMapping(APIHostPortsResult)
    async def APIHostPorts(self):
        '''

        Returns -> typing.Sequence[~HostPort]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='APIHostPorts', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIHostPorts)



    #@ReturnMapping(BytesResult)
    async def CACert(self):
        '''

        Returns -> typing.Sequence[int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='CACert', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CACert)



    #@ReturnMapping(DeployerConnectionValues)
    async def ConnectionInfo(self):
        '''

        Returns -> typing.Sequence[str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='ConnectionInfo', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ConnectionInfo)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='Life', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(StringResult)
    async def ModelUUID(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='ModelUUID', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelUUID)



    #@ReturnMapping(ErrorResults)
    async def Remove(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='Remove', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Remove)



    #@ReturnMapping(ErrorResults)
    async def SetPasswords(self, changes):
        '''
        changes : typing.Sequence[~EntityPassword]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='SetPasswords', Version=1, Params=params)
        params['Changes'] = changes
        reply = await self.rpc(msg)
        return self._map(reply, SetPasswords)



    #@ReturnMapping(StringsResult)
    async def StateAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='StateAddresses', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, StateAddresses)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchAPIHostPorts(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='WatchAPIHostPorts', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAPIHostPorts)



    #@ReturnMapping(StringsWatchResults)
    async def WatchUnits(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Deployer', Request='WatchUnits', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchUnits)


class DiscoverSpaces(Type):
    name = 'DiscoverSpaces'
    version = 2
    schema =     {'definitions': {'AddSubnetParams': {'additionalProperties': False,
                                         'properties': {'SpaceTag': {'type': 'string'},
                                                        'SubnetProviderId': {'type': 'string'},
                                                        'SubnetTag': {'type': 'string'},
                                                        'Zones': {'items': {'type': 'string'},
                                                                  'type': 'array'}},
                                         'required': ['SpaceTag'],
                                         'type': 'object'},
                     'AddSubnetsParams': {'additionalProperties': False,
                                          'properties': {'Subnets': {'items': {'$ref': '#/definitions/AddSubnetParams'},
                                                                     'type': 'array'}},
                                          'required': ['Subnets'],
                                          'type': 'object'},
                     'CreateSpaceParams': {'additionalProperties': False,
                                           'properties': {'ProviderId': {'type': 'string'},
                                                          'Public': {'type': 'boolean'},
                                                          'SpaceTag': {'type': 'string'},
                                                          'SubnetTags': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                           'required': ['SubnetTags',
                                                        'SpaceTag',
                                                        'Public'],
                                           'type': 'object'},
                     'CreateSpacesParams': {'additionalProperties': False,
                                            'properties': {'Spaces': {'items': {'$ref': '#/definitions/CreateSpaceParams'},
                                                                      'type': 'array'}},
                                            'required': ['Spaces'],
                                            'type': 'object'},
                     'DiscoverSpacesResults': {'additionalProperties': False,
                                               'properties': {'Results': {'items': {'$ref': '#/definitions/ProviderSpace'},
                                                                          'type': 'array'}},
                                               'required': ['Results'],
                                               'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ListSubnetsResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/Subnet'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'ProviderSpace': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Name': {'type': 'string'},
                                                      'ProviderId': {'type': 'string'},
                                                      'Subnets': {'items': {'$ref': '#/definitions/Subnet'},
                                                                  'type': 'array'}},
                                       'required': ['Name',
                                                    'ProviderId',
                                                    'Subnets'],
                                       'type': 'object'},
                     'Subnet': {'additionalProperties': False,
                                'properties': {'CIDR': {'type': 'string'},
                                               'Life': {'type': 'string'},
                                               'ProviderId': {'type': 'string'},
                                               'SpaceTag': {'type': 'string'},
                                               'StaticRangeHighIP': {'items': {'type': 'integer'},
                                                                     'type': 'array'},
                                               'StaticRangeLowIP': {'items': {'type': 'integer'},
                                                                    'type': 'array'},
                                               'Status': {'type': 'string'},
                                               'VLANTag': {'type': 'integer'},
                                               'Zones': {'items': {'type': 'string'},
                                                         'type': 'array'}},
                                'required': ['CIDR',
                                             'VLANTag',
                                             'Life',
                                             'SpaceTag',
                                             'Zones'],
                                'type': 'object'},
                     'SubnetsFilters': {'additionalProperties': False,
                                        'properties': {'SpaceTag': {'type': 'string'},
                                                       'Zone': {'type': 'string'}},
                                        'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddSubnets': {'properties': {'Params': {'$ref': '#/definitions/AddSubnetsParams'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'CreateSpaces': {'properties': {'Params': {'$ref': '#/definitions/CreateSpacesParams'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'ListSpaces': {'properties': {'Result': {'$ref': '#/definitions/DiscoverSpacesResults'}},
                                   'type': 'object'},
                    'ListSubnets': {'properties': {'Params': {'$ref': '#/definitions/SubnetsFilters'},
                                                   'Result': {'$ref': '#/definitions/ListSubnetsResults'}},
                                    'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AddSubnets(self, subnets):
        '''
        subnets : typing.Sequence[~AddSubnetParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiscoverSpaces', Request='AddSubnets', Version=2, Params=params)
        params['Subnets'] = subnets
        reply = await self.rpc(msg)
        return self._map(reply, AddSubnets)



    #@ReturnMapping(ErrorResults)
    async def CreateSpaces(self, spaces):
        '''
        spaces : typing.Sequence[~CreateSpaceParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiscoverSpaces', Request='CreateSpaces', Version=2, Params=params)
        params['Spaces'] = spaces
        reply = await self.rpc(msg)
        return self._map(reply, CreateSpaces)



    #@ReturnMapping(DiscoverSpacesResults)
    async def ListSpaces(self):
        '''

        Returns -> typing.Sequence[~ProviderSpace]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiscoverSpaces', Request='ListSpaces', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ListSpaces)



    #@ReturnMapping(ListSubnetsResults)
    async def ListSubnets(self, spacetag, zone):
        '''
        spacetag : str
        zone : str
        Returns -> typing.Sequence[~Subnet]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiscoverSpaces', Request='ListSubnets', Version=2, Params=params)
        params['SpaceTag'] = spacetag
        params['Zone'] = zone
        reply = await self.rpc(msg)
        return self._map(reply, ListSubnets)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiscoverSpaces', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)


class DiskManager(Type):
    name = 'DiskManager'
    version = 2
    schema =     {'definitions': {'BlockDevice': {'additionalProperties': False,
                                     'properties': {'BusAddress': {'type': 'string'},
                                                    'DeviceLinks': {'items': {'type': 'string'},
                                                                    'type': 'array'},
                                                    'DeviceName': {'type': 'string'},
                                                    'FilesystemType': {'type': 'string'},
                                                    'HardwareId': {'type': 'string'},
                                                    'InUse': {'type': 'boolean'},
                                                    'Label': {'type': 'string'},
                                                    'MountPoint': {'type': 'string'},
                                                    'Size': {'type': 'integer'},
                                                    'UUID': {'type': 'string'}},
                                     'required': ['DeviceName',
                                                  'DeviceLinks',
                                                  'Label',
                                                  'UUID',
                                                  'HardwareId',
                                                  'BusAddress',
                                                  'Size',
                                                  'FilesystemType',
                                                  'InUse',
                                                  'MountPoint'],
                                     'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineBlockDevices': {'additionalProperties': False,
                                             'properties': {'blockdevices': {'items': {'$ref': '#/definitions/BlockDevice'},
                                                                             'type': 'array'},
                                                            'machine': {'type': 'string'}},
                                             'required': ['machine'],
                                             'type': 'object'},
                     'SetMachineBlockDevices': {'additionalProperties': False,
                                                'properties': {'machineblockdevices': {'items': {'$ref': '#/definitions/MachineBlockDevices'},
                                                                                       'type': 'array'}},
                                                'required': ['machineblockdevices'],
                                                'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'SetMachineBlockDevices': {'properties': {'Params': {'$ref': '#/definitions/SetMachineBlockDevices'},
                                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                                               'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def SetMachineBlockDevices(self, machineblockdevices):
        '''
        machineblockdevices : typing.Sequence[~MachineBlockDevices]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='DiskManager', Request='SetMachineBlockDevices', Version=2, Params=params)
        params['machineblockdevices'] = machineblockdevices
        reply = await self.rpc(msg)
        return self._map(reply, SetMachineBlockDevices)


class EntityWatcher(Type):
    name = 'EntityWatcher'
    version = 2
    schema =     {'definitions': {'EntitiesWatchResult': {'additionalProperties': False,
                                             'properties': {'Changes': {'items': {'type': 'string'},
                                                                        'type': 'array'},
                                                            'EntityWatcherId': {'type': 'string'},
                                                            'Error': {'$ref': '#/definitions/Error'}},
                                             'required': ['EntityWatcherId',
                                                          'Changes',
                                                          'Error'],
                                             'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/EntitiesWatchResult'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(EntitiesWatchResult)
    async def Next(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='EntityWatcher', Request='Next', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='EntityWatcher', Request='Stop', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class FilesystemAttachmentsWatcher(Type):
    name = 'FilesystemAttachmentsWatcher'
    version = 2
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineStorageId': {'additionalProperties': False,
                                          'properties': {'attachmenttag': {'type': 'string'},
                                                         'machinetag': {'type': 'string'}},
                                          'required': ['machinetag',
                                                       'attachmenttag'],
                                          'type': 'object'},
                     'MachineStorageIdsWatchResult': {'additionalProperties': False,
                                                      'properties': {'Changes': {'items': {'$ref': '#/definitions/MachineStorageId'},
                                                                                 'type': 'array'},
                                                                     'Error': {'$ref': '#/definitions/Error'},
                                                                     'MachineStorageIdsWatcherId': {'type': 'string'}},
                                                      'required': ['MachineStorageIdsWatcherId',
                                                                   'Changes',
                                                                   'Error'],
                                                      'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/MachineStorageIdsWatchResult'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(MachineStorageIdsWatchResult)
    async def Next(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[~MachineStorageId]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='FilesystemAttachmentsWatcher', Request='Next', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='FilesystemAttachmentsWatcher', Request='Stop', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Firewaller(Type):
    name = 'Firewaller'
    version = 2
    schema =     {'definitions': {'BoolResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Result': {'type': 'boolean'}},
                                    'required': ['Error', 'Result'],
                                    'type': 'object'},
                     'BoolResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/BoolResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachinePortRange': {'additionalProperties': False,
                                          'properties': {'PortRange': {'$ref': '#/definitions/PortRange'},
                                                         'RelationTag': {'type': 'string'},
                                                         'UnitTag': {'type': 'string'}},
                                          'required': ['UnitTag',
                                                       'RelationTag',
                                                       'PortRange'],
                                          'type': 'object'},
                     'MachinePorts': {'additionalProperties': False,
                                      'properties': {'MachineTag': {'type': 'string'},
                                                     'SubnetTag': {'type': 'string'}},
                                      'required': ['MachineTag', 'SubnetTag'],
                                      'type': 'object'},
                     'MachinePortsParams': {'additionalProperties': False,
                                            'properties': {'Params': {'items': {'$ref': '#/definitions/MachinePorts'},
                                                                      'type': 'array'}},
                                            'required': ['Params'],
                                            'type': 'object'},
                     'MachinePortsResult': {'additionalProperties': False,
                                            'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                           'Ports': {'items': {'$ref': '#/definitions/MachinePortRange'},
                                                                     'type': 'array'}},
                                            'required': ['Error', 'Ports'],
                                            'type': 'object'},
                     'MachinePortsResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/MachinePortsResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'PortRange': {'additionalProperties': False,
                                   'properties': {'FromPort': {'type': 'integer'},
                                                  'Protocol': {'type': 'string'},
                                                  'ToPort': {'type': 'integer'}},
                                   'required': ['FromPort', 'ToPort', 'Protocol'],
                                   'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsResults': {'additionalProperties': False,
                                        'properties': {'Results': {'items': {'$ref': '#/definitions/StringsResult'},
                                                                   'type': 'array'}},
                                        'required': ['Results'],
                                        'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'GetAssignedMachine': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                          'Result': {'$ref': '#/definitions/StringResults'}},
                                           'type': 'object'},
                    'GetExposed': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/BoolResults'}},
                                   'type': 'object'},
                    'GetMachineActiveSubnets': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                               'Result': {'$ref': '#/definitions/StringsResults'}},
                                                'type': 'object'},
                    'GetMachinePorts': {'properties': {'Params': {'$ref': '#/definitions/MachinePortsParams'},
                                                       'Result': {'$ref': '#/definitions/MachinePortsResults'}},
                                        'type': 'object'},
                    'InstanceId': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringResults'}},
                                   'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'Watch': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                              'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'},
                    'WatchModelMachines': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                                           'type': 'object'},
                    'WatchOpenedPorts': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                         'type': 'object'},
                    'WatchUnits': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringResults)
    async def GetAssignedMachine(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='GetAssignedMachine', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetAssignedMachine)



    #@ReturnMapping(BoolResults)
    async def GetExposed(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~BoolResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='GetExposed', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetExposed)



    #@ReturnMapping(StringsResults)
    async def GetMachineActiveSubnets(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='GetMachineActiveSubnets', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetMachineActiveSubnets)



    #@ReturnMapping(MachinePortsResults)
    async def GetMachinePorts(self, params):
        '''
        params : typing.Sequence[~MachinePorts]
        Returns -> typing.Sequence[~MachinePortsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='GetMachinePorts', Version=2, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, GetMachinePorts)



    #@ReturnMapping(StringResults)
    async def InstanceId(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='InstanceId', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceId)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='Life', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(NotifyWatchResults)
    async def Watch(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='Watch', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Watch)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='WatchForModelConfigChanges', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)



    #@ReturnMapping(StringsWatchResult)
    async def WatchModelMachines(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='WatchModelMachines', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchModelMachines)



    #@ReturnMapping(StringsWatchResults)
    async def WatchOpenedPorts(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='WatchOpenedPorts', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchOpenedPorts)



    #@ReturnMapping(StringsWatchResults)
    async def WatchUnits(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Firewaller', Request='WatchUnits', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchUnits)


class HighAvailability(Type):
    name = 'HighAvailability'
    version = 2
    schema =     {'definitions': {'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'SpaceProviderId': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value',
                                              'Type',
                                              'Scope',
                                              'SpaceName',
                                              'SpaceProviderId'],
                                 'type': 'object'},
                     'ControllersChangeResult': {'additionalProperties': False,
                                                 'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                'Result': {'$ref': '#/definitions/ControllersChanges'}},
                                                 'required': ['Result', 'Error'],
                                                 'type': 'object'},
                     'ControllersChangeResults': {'additionalProperties': False,
                                                  'properties': {'Results': {'items': {'$ref': '#/definitions/ControllersChangeResult'},
                                                                             'type': 'array'}},
                                                  'required': ['Results'],
                                                  'type': 'object'},
                     'ControllersChanges': {'additionalProperties': False,
                                            'properties': {'added': {'items': {'type': 'string'},
                                                                     'type': 'array'},
                                                           'converted': {'items': {'type': 'string'},
                                                                         'type': 'array'},
                                                           'demoted': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'maintained': {'items': {'type': 'string'},
                                                                          'type': 'array'},
                                                           'promoted': {'items': {'type': 'string'},
                                                                        'type': 'array'},
                                                           'removed': {'items': {'type': 'string'},
                                                                       'type': 'array'}},
                                            'type': 'object'},
                     'ControllersSpec': {'additionalProperties': False,
                                         'properties': {'ModelTag': {'type': 'string'},
                                                        'constraints': {'$ref': '#/definitions/Value'},
                                                        'num-controllers': {'type': 'integer'},
                                                        'placement': {'items': {'type': 'string'},
                                                                      'type': 'array'},
                                                        'series': {'type': 'string'}},
                                         'required': ['ModelTag',
                                                      'num-controllers'],
                                         'type': 'object'},
                     'ControllersSpecs': {'additionalProperties': False,
                                          'properties': {'Specs': {'items': {'$ref': '#/definitions/ControllersSpec'},
                                                                   'type': 'array'}},
                                          'required': ['Specs'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'HAMember': {'additionalProperties': False,
                                  'properties': {'PublicAddress': {'$ref': '#/definitions/Address'},
                                                 'Series': {'type': 'string'},
                                                 'Tag': {'type': 'string'}},
                                  'required': ['Tag', 'PublicAddress', 'Series'],
                                  'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Member': {'additionalProperties': False,
                                'properties': {'Address': {'type': 'string'},
                                               'Arbiter': {'type': 'boolean'},
                                               'BuildIndexes': {'type': 'boolean'},
                                               'Hidden': {'type': 'boolean'},
                                               'Id': {'type': 'integer'},
                                               'Priority': {'type': 'number'},
                                               'SlaveDelay': {'type': 'integer'},
                                               'Tags': {'patternProperties': {'.*': {'type': 'string'}},
                                                        'type': 'object'},
                                               'Votes': {'type': 'integer'}},
                                'required': ['Id',
                                             'Address',
                                             'Arbiter',
                                             'BuildIndexes',
                                             'Hidden',
                                             'Priority',
                                             'Tags',
                                             'SlaveDelay',
                                             'Votes'],
                                'type': 'object'},
                     'MongoUpgradeResults': {'additionalProperties': False,
                                             'properties': {'Master': {'$ref': '#/definitions/HAMember'},
                                                            'Members': {'items': {'$ref': '#/definitions/HAMember'},
                                                                        'type': 'array'},
                                                            'RsMembers': {'items': {'$ref': '#/definitions/Member'},
                                                                          'type': 'array'}},
                                             'required': ['RsMembers',
                                                          'Master',
                                                          'Members'],
                                             'type': 'object'},
                     'ResumeReplicationParams': {'additionalProperties': False,
                                                 'properties': {'Members': {'items': {'$ref': '#/definitions/Member'},
                                                                            'type': 'array'}},
                                                 'required': ['Members'],
                                                 'type': 'object'},
                     'UpgradeMongoParams': {'additionalProperties': False,
                                            'properties': {'Target': {'$ref': '#/definitions/Version'}},
                                            'required': ['Target'],
                                            'type': 'object'},
                     'Value': {'additionalProperties': False,
                               'properties': {'arch': {'type': 'string'},
                                              'container': {'type': 'string'},
                                              'cpu-cores': {'type': 'integer'},
                                              'cpu-power': {'type': 'integer'},
                                              'instance-type': {'type': 'string'},
                                              'mem': {'type': 'integer'},
                                              'root-disk': {'type': 'integer'},
                                              'spaces': {'items': {'type': 'string'},
                                                         'type': 'array'},
                                              'tags': {'items': {'type': 'string'},
                                                       'type': 'array'},
                                              'virt-type': {'type': 'string'}},
                               'type': 'object'},
                     'Version': {'additionalProperties': False,
                                 'properties': {'Major': {'type': 'integer'},
                                                'Minor': {'type': 'integer'},
                                                'Patch': {'type': 'string'},
                                                'StorageEngine': {'type': 'string'}},
                                 'required': ['Major',
                                              'Minor',
                                              'Patch',
                                              'StorageEngine'],
                                 'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'EnableHA': {'properties': {'Params': {'$ref': '#/definitions/ControllersSpecs'},
                                                'Result': {'$ref': '#/definitions/ControllersChangeResults'}},
                                 'type': 'object'},
                    'ResumeHAReplicationAfterUpgrade': {'properties': {'Params': {'$ref': '#/definitions/ResumeReplicationParams'}},
                                                        'type': 'object'},
                    'StopHAReplicationForUpgrade': {'properties': {'Params': {'$ref': '#/definitions/UpgradeMongoParams'},
                                                                   'Result': {'$ref': '#/definitions/MongoUpgradeResults'}},
                                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ControllersChangeResults)
    async def EnableHA(self, specs):
        '''
        specs : typing.Sequence[~ControllersSpec]
        Returns -> typing.Sequence[~ControllersChangeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='HighAvailability', Request='EnableHA', Version=2, Params=params)
        params['Specs'] = specs
        reply = await self.rpc(msg)
        return self._map(reply, EnableHA)



    #@ReturnMapping(None)
    async def ResumeHAReplicationAfterUpgrade(self, members):
        '''
        members : typing.Sequence[~Member]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='HighAvailability', Request='ResumeHAReplicationAfterUpgrade', Version=2, Params=params)
        params['Members'] = members
        reply = await self.rpc(msg)
        return self._map(reply, ResumeHAReplicationAfterUpgrade)



    #@ReturnMapping(MongoUpgradeResults)
    async def StopHAReplicationForUpgrade(self, minor, patch, major, storageengine):
        '''
        minor : int
        patch : str
        major : int
        storageengine : str
        Returns -> typing.Union[~HAMember, typing.Sequence[~Member]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='HighAvailability', Request='StopHAReplicationForUpgrade', Version=2, Params=params)
        params['Minor'] = minor
        params['Patch'] = patch
        params['Major'] = major
        params['StorageEngine'] = storageengine
        reply = await self.rpc(msg)
        return self._map(reply, StopHAReplicationForUpgrade)


class HostKeyReporter(Type):
    name = 'HostKeyReporter'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'SSHHostKeySet': {'additionalProperties': False,
                                       'properties': {'entity-keys': {'items': {'$ref': '#/definitions/SSHHostKeys'},
                                                                      'type': 'array'}},
                                       'required': ['entity-keys'],
                                       'type': 'object'},
                     'SSHHostKeys': {'additionalProperties': False,
                                     'properties': {'public-keys': {'items': {'type': 'string'},
                                                                    'type': 'array'},
                                                    'tag': {'type': 'string'}},
                                     'required': ['tag', 'public-keys'],
                                     'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ReportKeys': {'properties': {'Params': {'$ref': '#/definitions/SSHHostKeySet'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def ReportKeys(self, entity_keys):
        '''
        entity_keys : typing.Sequence[~SSHHostKeys]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='HostKeyReporter', Request='ReportKeys', Version=1, Params=params)
        params['entity-keys'] = entity_keys
        reply = await self.rpc(msg)
        return self._map(reply, ReportKeys)


class ImageManager(Type):
    name = 'ImageManager'
    version = 2
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ImageFilterParams': {'additionalProperties': False,
                                           'properties': {'images': {'items': {'$ref': '#/definitions/ImageSpec'},
                                                                     'type': 'array'}},
                                           'required': ['images'],
                                           'type': 'object'},
                     'ImageMetadata': {'additionalProperties': False,
                                       'properties': {'arch': {'type': 'string'},
                                                      'created': {'format': 'date-time',
                                                                  'type': 'string'},
                                                      'kind': {'type': 'string'},
                                                      'series': {'type': 'string'},
                                                      'url': {'type': 'string'}},
                                       'required': ['kind',
                                                    'arch',
                                                    'series',
                                                    'url',
                                                    'created'],
                                       'type': 'object'},
                     'ImageSpec': {'additionalProperties': False,
                                   'properties': {'arch': {'type': 'string'},
                                                  'kind': {'type': 'string'},
                                                  'series': {'type': 'string'}},
                                   'required': ['kind', 'arch', 'series'],
                                   'type': 'object'},
                     'ListImageResult': {'additionalProperties': False,
                                         'properties': {'result': {'items': {'$ref': '#/definitions/ImageMetadata'},
                                                                   'type': 'array'}},
                                         'required': ['result'],
                                         'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'DeleteImages': {'properties': {'Params': {'$ref': '#/definitions/ImageFilterParams'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'ListImages': {'properties': {'Params': {'$ref': '#/definitions/ImageFilterParams'},
                                                  'Result': {'$ref': '#/definitions/ListImageResult'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def DeleteImages(self, images):
        '''
        images : typing.Sequence[~ImageSpec]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageManager', Request='DeleteImages', Version=2, Params=params)
        params['images'] = images
        reply = await self.rpc(msg)
        return self._map(reply, DeleteImages)



    #@ReturnMapping(ListImageResult)
    async def ListImages(self, images):
        '''
        images : typing.Sequence[~ImageSpec]
        Returns -> typing.Sequence[~ImageMetadata]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageManager', Request='ListImages', Version=2, Params=params)
        params['images'] = images
        reply = await self.rpc(msg)
        return self._map(reply, ListImages)


class ImageMetadata(Type):
    name = 'ImageMetadata'
    version = 2
    schema =     {'definitions': {'CloudImageMetadata': {'additionalProperties': False,
                                            'properties': {'arch': {'type': 'string'},
                                                           'image_id': {'type': 'string'},
                                                           'priority': {'type': 'integer'},
                                                           'region': {'type': 'string'},
                                                           'root_storage_size': {'type': 'integer'},
                                                           'root_storage_type': {'type': 'string'},
                                                           'series': {'type': 'string'},
                                                           'source': {'type': 'string'},
                                                           'stream': {'type': 'string'},
                                                           'version': {'type': 'string'},
                                                           'virt_type': {'type': 'string'}},
                                            'required': ['image_id',
                                                         'region',
                                                         'version',
                                                         'series',
                                                         'arch',
                                                         'source',
                                                         'priority'],
                                            'type': 'object'},
                     'CloudImageMetadataList': {'additionalProperties': False,
                                                'properties': {'metadata': {'items': {'$ref': '#/definitions/CloudImageMetadata'},
                                                                            'type': 'array'}},
                                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ImageMetadataFilter': {'additionalProperties': False,
                                             'properties': {'arches': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                            'region': {'type': 'string'},
                                                            'root-storage-type': {'type': 'string'},
                                                            'series': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                            'stream': {'type': 'string'},
                                                            'virt_type': {'type': 'string'}},
                                             'type': 'object'},
                     'ListCloudImageMetadataResult': {'additionalProperties': False,
                                                      'properties': {'result': {'items': {'$ref': '#/definitions/CloudImageMetadata'},
                                                                                'type': 'array'}},
                                                      'required': ['result'],
                                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MetadataImageIds': {'additionalProperties': False,
                                          'properties': {'image_ids': {'items': {'type': 'string'},
                                                                       'type': 'array'}},
                                          'required': ['image_ids'],
                                          'type': 'object'},
                     'MetadataSaveParams': {'additionalProperties': False,
                                            'properties': {'metadata': {'items': {'$ref': '#/definitions/CloudImageMetadataList'},
                                                                        'type': 'array'}},
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Delete': {'properties': {'Params': {'$ref': '#/definitions/MetadataImageIds'},
                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                               'type': 'object'},
                    'List': {'properties': {'Params': {'$ref': '#/definitions/ImageMetadataFilter'},
                                            'Result': {'$ref': '#/definitions/ListCloudImageMetadataResult'}},
                             'type': 'object'},
                    'Save': {'properties': {'Params': {'$ref': '#/definitions/MetadataSaveParams'},
                                            'Result': {'$ref': '#/definitions/ErrorResults'}},
                             'type': 'object'},
                    'UpdateFromPublishedImages': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def Delete(self, image_ids):
        '''
        image_ids : typing.Sequence[str]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageMetadata', Request='Delete', Version=2, Params=params)
        params['image_ids'] = image_ids
        reply = await self.rpc(msg)
        return self._map(reply, Delete)



    #@ReturnMapping(ListCloudImageMetadataResult)
    async def List(self, root_storage_type, arches, virt_type, series, stream, region):
        '''
        root_storage_type : str
        arches : typing.Sequence[str]
        virt_type : str
        series : typing.Sequence[str]
        stream : str
        region : str
        Returns -> typing.Sequence[~CloudImageMetadata]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageMetadata', Request='List', Version=2, Params=params)
        params['root-storage-type'] = root_storage_type
        params['arches'] = arches
        params['virt_type'] = virt_type
        params['series'] = series
        params['stream'] = stream
        params['region'] = region
        reply = await self.rpc(msg)
        return self._map(reply, List)



    #@ReturnMapping(ErrorResults)
    async def Save(self, metadata):
        '''
        metadata : typing.Sequence[~CloudImageMetadataList]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageMetadata', Request='Save', Version=2, Params=params)
        params['metadata'] = metadata
        reply = await self.rpc(msg)
        return self._map(reply, Save)



    #@ReturnMapping(None)
    async def UpdateFromPublishedImages(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ImageMetadata', Request='UpdateFromPublishedImages', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, UpdateFromPublishedImages)


class InstancePoller(Type):
    name = 'InstancePoller'
    version = 2
    schema =     {'definitions': {'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'BoolResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Result': {'type': 'boolean'}},
                                    'required': ['Error', 'Result'],
                                    'type': 'object'},
                     'BoolResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/BoolResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineAddresses': {'additionalProperties': False,
                                          'properties': {'Addresses': {'items': {'$ref': '#/definitions/Address'},
                                                                       'type': 'array'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag', 'Addresses'],
                                          'type': 'object'},
                     'MachineAddressesResult': {'additionalProperties': False,
                                                'properties': {'Addresses': {'items': {'$ref': '#/definitions/Address'},
                                                                             'type': 'array'},
                                                               'Error': {'$ref': '#/definitions/Error'}},
                                                'required': ['Error', 'Addresses'],
                                                'type': 'object'},
                     'MachineAddressesResults': {'additionalProperties': False,
                                                 'properties': {'Results': {'items': {'$ref': '#/definitions/MachineAddressesResult'},
                                                                            'type': 'array'}},
                                                 'required': ['Results'],
                                                 'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'SetMachinesAddresses': {'additionalProperties': False,
                                              'properties': {'MachineAddresses': {'items': {'$ref': '#/definitions/MachineAddresses'},
                                                                                  'type': 'array'}},
                                              'required': ['MachineAddresses'],
                                              'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'StatusResult': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Error': {'$ref': '#/definitions/Error'},
                                                     'Id': {'type': 'string'},
                                                     'Info': {'type': 'string'},
                                                     'Life': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Error',
                                                   'Id',
                                                   'Life',
                                                   'Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'StatusResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StatusResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AreManuallyProvisioned': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                              'Result': {'$ref': '#/definitions/BoolResults'}},
                                               'type': 'object'},
                    'InstanceId': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringResults'}},
                                   'type': 'object'},
                    'InstanceStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/StatusResults'}},
                                       'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'ProviderAddresses': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                         'Result': {'$ref': '#/definitions/MachineAddressesResults'}},
                                          'type': 'object'},
                    'SetInstanceStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'},
                    'SetProviderAddresses': {'properties': {'Params': {'$ref': '#/definitions/SetMachinesAddresses'},
                                                            'Result': {'$ref': '#/definitions/ErrorResults'}},
                                             'type': 'object'},
                    'Status': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/StatusResults'}},
                               'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'},
                    'WatchModelMachines': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                                           'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(BoolResults)
    async def AreManuallyProvisioned(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~BoolResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='AreManuallyProvisioned', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AreManuallyProvisioned)



    #@ReturnMapping(StringResults)
    async def InstanceId(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='InstanceId', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceId)



    #@ReturnMapping(StatusResults)
    async def InstanceStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='InstanceStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceStatus)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='Life', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(MachineAddressesResults)
    async def ProviderAddresses(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachineAddressesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='ProviderAddresses', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ProviderAddresses)



    #@ReturnMapping(ErrorResults)
    async def SetInstanceStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='SetInstanceStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetInstanceStatus)



    #@ReturnMapping(ErrorResults)
    async def SetProviderAddresses(self, machineaddresses):
        '''
        machineaddresses : typing.Sequence[~MachineAddresses]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='SetProviderAddresses', Version=2, Params=params)
        params['MachineAddresses'] = machineaddresses
        reply = await self.rpc(msg)
        return self._map(reply, SetProviderAddresses)



    #@ReturnMapping(StatusResults)
    async def Status(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='Status', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Status)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='WatchForModelConfigChanges', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)



    #@ReturnMapping(StringsWatchResult)
    async def WatchModelMachines(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='InstancePoller', Request='WatchModelMachines', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchModelMachines)


class KeyManager(Type):
    name = 'KeyManager'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ListSSHKeys': {'additionalProperties': False,
                                     'properties': {'Entities': {'$ref': '#/definitions/Entities'},
                                                    'Mode': {'type': 'boolean'}},
                                     'required': ['Entities', 'Mode'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ModifyUserSSHKeys': {'additionalProperties': False,
                                           'properties': {'Keys': {'items': {'type': 'string'},
                                                                   'type': 'array'},
                                                          'User': {'type': 'string'}},
                                           'required': ['User', 'Keys'],
                                           'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsResults': {'additionalProperties': False,
                                        'properties': {'Results': {'items': {'$ref': '#/definitions/StringsResult'},
                                                                   'type': 'array'}},
                                        'required': ['Results'],
                                        'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddKeys': {'properties': {'Params': {'$ref': '#/definitions/ModifyUserSSHKeys'},
                                               'Result': {'$ref': '#/definitions/ErrorResults'}},
                                'type': 'object'},
                    'DeleteKeys': {'properties': {'Params': {'$ref': '#/definitions/ModifyUserSSHKeys'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'ImportKeys': {'properties': {'Params': {'$ref': '#/definitions/ModifyUserSSHKeys'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'ListKeys': {'properties': {'Params': {'$ref': '#/definitions/ListSSHKeys'},
                                                'Result': {'$ref': '#/definitions/StringsResults'}},
                                 'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AddKeys(self, user, keys):
        '''
        user : str
        keys : typing.Sequence[str]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyManager', Request='AddKeys', Version=1, Params=params)
        params['User'] = user
        params['Keys'] = keys
        reply = await self.rpc(msg)
        return self._map(reply, AddKeys)



    #@ReturnMapping(ErrorResults)
    async def DeleteKeys(self, user, keys):
        '''
        user : str
        keys : typing.Sequence[str]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyManager', Request='DeleteKeys', Version=1, Params=params)
        params['User'] = user
        params['Keys'] = keys
        reply = await self.rpc(msg)
        return self._map(reply, DeleteKeys)



    #@ReturnMapping(ErrorResults)
    async def ImportKeys(self, user, keys):
        '''
        user : str
        keys : typing.Sequence[str]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyManager', Request='ImportKeys', Version=1, Params=params)
        params['User'] = user
        params['Keys'] = keys
        reply = await self.rpc(msg)
        return self._map(reply, ImportKeys)



    #@ReturnMapping(StringsResults)
    async def ListKeys(self, entities, mode):
        '''
        entities : ~Entities
        mode : bool
        Returns -> typing.Sequence[~StringsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyManager', Request='ListKeys', Version=1, Params=params)
        params['Entities'] = entities
        params['Mode'] = mode
        reply = await self.rpc(msg)
        return self._map(reply, ListKeys)


class KeyUpdater(Type):
    name = 'KeyUpdater'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsResults': {'additionalProperties': False,
                                        'properties': {'Results': {'items': {'$ref': '#/definitions/StringsResult'},
                                                                   'type': 'array'}},
                                        'required': ['Results'],
                                        'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AuthorisedKeys': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/StringsResults'}},
                                       'type': 'object'},
                    'WatchAuthorisedKeys': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                           'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                            'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsResults)
    async def AuthorisedKeys(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyUpdater', Request='AuthorisedKeys', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AuthorisedKeys)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchAuthorisedKeys(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='KeyUpdater', Request='WatchAuthorisedKeys', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchAuthorisedKeys)


class LeadershipService(Type):
    name = 'LeadershipService'
    version = 2
    schema =     {'definitions': {'ClaimLeadershipBulkParams': {'additionalProperties': False,
                                                   'properties': {'Params': {'items': {'$ref': '#/definitions/ClaimLeadershipParams'},
                                                                             'type': 'array'}},
                                                   'required': ['Params'],
                                                   'type': 'object'},
                     'ClaimLeadershipBulkResults': {'additionalProperties': False,
                                                    'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                               'type': 'array'}},
                                                    'required': ['Results'],
                                                    'type': 'object'},
                     'ClaimLeadershipParams': {'additionalProperties': False,
                                               'properties': {'DurationSeconds': {'type': 'number'},
                                                              'ServiceTag': {'type': 'string'},
                                                              'UnitTag': {'type': 'string'}},
                                               'required': ['ServiceTag',
                                                            'UnitTag',
                                                            'DurationSeconds'],
                                               'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ServiceTag': {'additionalProperties': False,
                                    'properties': {'Name': {'type': 'string'}},
                                    'required': ['Name'],
                                    'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'BlockUntilLeadershipReleased': {'properties': {'Params': {'$ref': '#/definitions/ServiceTag'},
                                                                    'Result': {'$ref': '#/definitions/ErrorResult'}},
                                                     'type': 'object'},
                    'ClaimLeadership': {'properties': {'Params': {'$ref': '#/definitions/ClaimLeadershipBulkParams'},
                                                       'Result': {'$ref': '#/definitions/ClaimLeadershipBulkResults'}},
                                        'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResult)
    async def BlockUntilLeadershipReleased(self, name):
        '''
        name : str
        Returns -> ~Error
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='LeadershipService', Request='BlockUntilLeadershipReleased', Version=2, Params=params)
        params['Name'] = name
        reply = await self.rpc(msg)
        return self._map(reply, BlockUntilLeadershipReleased)



    #@ReturnMapping(ClaimLeadershipBulkResults)
    async def ClaimLeadership(self, params):
        '''
        params : typing.Sequence[~ClaimLeadershipParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='LeadershipService', Request='ClaimLeadership', Version=2, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, ClaimLeadership)


class LifeFlag(Type):
    name = 'LifeFlag'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'Watch': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='LifeFlag', Request='Life', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(NotifyWatchResults)
    async def Watch(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='LifeFlag', Request='Watch', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Watch)


class Logger(Type):
    name = 'Logger'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'LoggingConfig': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/StringResults'}},
                                      'type': 'object'},
                    'WatchLoggingConfig': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                          'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                           'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringResults)
    async def LoggingConfig(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Logger', Request='LoggingConfig', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, LoggingConfig)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchLoggingConfig(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Logger', Request='WatchLoggingConfig', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchLoggingConfig)


class MachineActions(Type):
    name = 'MachineActions'
    version = 1
    schema =     {'definitions': {'Action': {'additionalProperties': False,
                                'properties': {'name': {'type': 'string'},
                                               'parameters': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                               'receiver': {'type': 'string'},
                                               'tag': {'type': 'string'}},
                                'required': ['tag', 'receiver', 'name'],
                                'type': 'object'},
                     'ActionExecutionResult': {'additionalProperties': False,
                                               'properties': {'actiontag': {'type': 'string'},
                                                              'message': {'type': 'string'},
                                                              'results': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                       'type': 'object'}},
                                                                          'type': 'object'},
                                                              'status': {'type': 'string'}},
                                               'required': ['actiontag', 'status'],
                                               'type': 'object'},
                     'ActionExecutionResults': {'additionalProperties': False,
                                                'properties': {'results': {'items': {'$ref': '#/definitions/ActionExecutionResult'},
                                                                           'type': 'array'}},
                                                'type': 'object'},
                     'ActionResult': {'additionalProperties': False,
                                      'properties': {'action': {'$ref': '#/definitions/Action'},
                                                     'completed': {'format': 'date-time',
                                                                   'type': 'string'},
                                                     'enqueued': {'format': 'date-time',
                                                                  'type': 'string'},
                                                     'error': {'$ref': '#/definitions/Error'},
                                                     'message': {'type': 'string'},
                                                     'output': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                             'type': 'object'}},
                                                                'type': 'object'},
                                                     'started': {'format': 'date-time',
                                                                 'type': 'string'},
                                                     'status': {'type': 'string'}},
                                      'type': 'object'},
                     'ActionResults': {'additionalProperties': False,
                                       'properties': {'results': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'ActionsByReceiver': {'additionalProperties': False,
                                           'properties': {'actions': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                      'type': 'array'},
                                                          'error': {'$ref': '#/definitions/Error'},
                                                          'receiver': {'type': 'string'}},
                                           'type': 'object'},
                     'ActionsByReceivers': {'additionalProperties': False,
                                            'properties': {'actions': {'items': {'$ref': '#/definitions/ActionsByReceiver'},
                                                                       'type': 'array'}},
                                            'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Actions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ActionResults'}},
                                'type': 'object'},
                    'BeginActions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'FinishActions': {'properties': {'Params': {'$ref': '#/definitions/ActionExecutionResults'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'RunningActions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/ActionsByReceivers'}},
                                       'type': 'object'},
                    'WatchActionNotifications': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                                 'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ActionResults)
    async def Actions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineActions', Request='Actions', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Actions)



    #@ReturnMapping(ErrorResults)
    async def BeginActions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineActions', Request='BeginActions', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, BeginActions)



    #@ReturnMapping(ErrorResults)
    async def FinishActions(self, results):
        '''
        results : typing.Sequence[~ActionExecutionResult]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineActions', Request='FinishActions', Version=1, Params=params)
        params['results'] = results
        reply = await self.rpc(msg)
        return self._map(reply, FinishActions)



    #@ReturnMapping(ActionsByReceivers)
    async def RunningActions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionsByReceiver]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineActions', Request='RunningActions', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, RunningActions)



    #@ReturnMapping(StringsWatchResults)
    async def WatchActionNotifications(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineActions', Request='WatchActionNotifications', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchActionNotifications)


class MachineManager(Type):
    name = 'MachineManager'
    version = 2
    schema =     {'definitions': {'AddMachineParams': {'additionalProperties': False,
                                          'properties': {'Addrs': {'items': {'$ref': '#/definitions/Address'},
                                                                   'type': 'array'},
                                                         'Constraints': {'$ref': '#/definitions/Value'},
                                                         'ContainerType': {'type': 'string'},
                                                         'Disks': {'items': {'$ref': '#/definitions/Constraints'},
                                                                   'type': 'array'},
                                                         'HardwareCharacteristics': {'$ref': '#/definitions/HardwareCharacteristics'},
                                                         'InstanceId': {'type': 'string'},
                                                         'Jobs': {'items': {'type': 'string'},
                                                                  'type': 'array'},
                                                         'Nonce': {'type': 'string'},
                                                         'ParentId': {'type': 'string'},
                                                         'Placement': {'$ref': '#/definitions/Placement'},
                                                         'Series': {'type': 'string'}},
                                          'required': ['Series',
                                                       'Constraints',
                                                       'Jobs',
                                                       'Disks',
                                                       'Placement',
                                                       'ParentId',
                                                       'ContainerType',
                                                       'InstanceId',
                                                       'Nonce',
                                                       'HardwareCharacteristics',
                                                       'Addrs'],
                                          'type': 'object'},
                     'AddMachines': {'additionalProperties': False,
                                     'properties': {'MachineParams': {'items': {'$ref': '#/definitions/AddMachineParams'},
                                                                      'type': 'array'}},
                                     'required': ['MachineParams'],
                                     'type': 'object'},
                     'AddMachinesResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'Machine': {'type': 'string'}},
                                           'required': ['Machine', 'Error'],
                                           'type': 'object'},
                     'AddMachinesResults': {'additionalProperties': False,
                                            'properties': {'Machines': {'items': {'$ref': '#/definitions/AddMachinesResult'},
                                                                        'type': 'array'}},
                                            'required': ['Machines'],
                                            'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'Constraints': {'additionalProperties': False,
                                     'properties': {'Count': {'type': 'integer'},
                                                    'Pool': {'type': 'string'},
                                                    'Size': {'type': 'integer'}},
                                     'required': ['Pool', 'Size', 'Count'],
                                     'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'HardwareCharacteristics': {'additionalProperties': False,
                                                 'properties': {'Arch': {'type': 'string'},
                                                                'AvailabilityZone': {'type': 'string'},
                                                                'CpuCores': {'type': 'integer'},
                                                                'CpuPower': {'type': 'integer'},
                                                                'Mem': {'type': 'integer'},
                                                                'RootDisk': {'type': 'integer'},
                                                                'Tags': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                                 'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Placement': {'additionalProperties': False,
                                   'properties': {'Directive': {'type': 'string'},
                                                  'Scope': {'type': 'string'}},
                                   'required': ['Scope', 'Directive'],
                                   'type': 'object'},
                     'Value': {'additionalProperties': False,
                               'properties': {'arch': {'type': 'string'},
                                              'container': {'type': 'string'},
                                              'cpu-cores': {'type': 'integer'},
                                              'cpu-power': {'type': 'integer'},
                                              'instance-type': {'type': 'string'},
                                              'mem': {'type': 'integer'},
                                              'root-disk': {'type': 'integer'},
                                              'spaces': {'items': {'type': 'string'},
                                                         'type': 'array'},
                                              'tags': {'items': {'type': 'string'},
                                                       'type': 'array'},
                                              'virt-type': {'type': 'string'}},
                               'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddMachines': {'properties': {'Params': {'$ref': '#/definitions/AddMachines'},
                                                   'Result': {'$ref': '#/definitions/AddMachinesResults'}},
                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AddMachinesResults)
    async def AddMachines(self, machineparams):
        '''
        machineparams : typing.Sequence[~AddMachineParams]
        Returns -> typing.Sequence[~AddMachinesResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MachineManager', Request='AddMachines', Version=2, Params=params)
        params['MachineParams'] = machineparams
        reply = await self.rpc(msg)
        return self._map(reply, AddMachines)


class Machiner(Type):
    name = 'Machiner'
    version = 1
    schema =     {'definitions': {'APIHostPortsResult': {'additionalProperties': False,
                                            'properties': {'Servers': {'items': {'items': {'$ref': '#/definitions/HostPort'},
                                                                                 'type': 'array'},
                                                                       'type': 'array'}},
                                            'required': ['Servers'],
                                            'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'BytesResult': {'additionalProperties': False,
                                     'properties': {'Result': {'items': {'type': 'integer'},
                                                               'type': 'array'}},
                                     'required': ['Result'],
                                     'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'HostPort': {'additionalProperties': False,
                                  'properties': {'Address': {'$ref': '#/definitions/Address'},
                                                 'Port': {'type': 'integer'}},
                                  'required': ['Address', 'Port'],
                                  'type': 'object'},
                     'JobsResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Jobs': {'items': {'type': 'string'},
                                                            'type': 'array'}},
                                    'required': ['Jobs', 'Error'],
                                    'type': 'object'},
                     'JobsResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/JobsResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineAddresses': {'additionalProperties': False,
                                          'properties': {'Addresses': {'items': {'$ref': '#/definitions/Address'},
                                                                       'type': 'array'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag', 'Addresses'],
                                          'type': 'object'},
                     'NetworkConfig': {'additionalProperties': False,
                                       'properties': {'Address': {'type': 'string'},
                                                      'CIDR': {'type': 'string'},
                                                      'ConfigType': {'type': 'string'},
                                                      'DNSSearchDomains': {'items': {'type': 'string'},
                                                                           'type': 'array'},
                                                      'DNSServers': {'items': {'type': 'string'},
                                                                     'type': 'array'},
                                                      'DeviceIndex': {'type': 'integer'},
                                                      'Disabled': {'type': 'boolean'},
                                                      'GatewayAddress': {'type': 'string'},
                                                      'InterfaceName': {'type': 'string'},
                                                      'InterfaceType': {'type': 'string'},
                                                      'MACAddress': {'type': 'string'},
                                                      'MTU': {'type': 'integer'},
                                                      'NoAutoStart': {'type': 'boolean'},
                                                      'ParentInterfaceName': {'type': 'string'},
                                                      'ProviderAddressId': {'type': 'string'},
                                                      'ProviderId': {'type': 'string'},
                                                      'ProviderSpaceId': {'type': 'string'},
                                                      'ProviderSubnetId': {'type': 'string'},
                                                      'ProviderVLANId': {'type': 'string'},
                                                      'VLANTag': {'type': 'integer'}},
                                       'required': ['DeviceIndex',
                                                    'MACAddress',
                                                    'CIDR',
                                                    'MTU',
                                                    'ProviderId',
                                                    'ProviderSubnetId',
                                                    'ProviderSpaceId',
                                                    'ProviderAddressId',
                                                    'ProviderVLANId',
                                                    'VLANTag',
                                                    'InterfaceName',
                                                    'ParentInterfaceName',
                                                    'InterfaceType',
                                                    'Disabled'],
                                       'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'SetMachineNetworkConfig': {'additionalProperties': False,
                                                 'properties': {'Config': {'items': {'$ref': '#/definitions/NetworkConfig'},
                                                                           'type': 'array'},
                                                                'Tag': {'type': 'string'}},
                                                 'required': ['Tag', 'Config'],
                                                 'type': 'object'},
                     'SetMachinesAddresses': {'additionalProperties': False,
                                              'properties': {'MachineAddresses': {'items': {'$ref': '#/definitions/MachineAddresses'},
                                                                                  'type': 'array'}},
                                              'required': ['MachineAddresses'],
                                              'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'APIAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                     'type': 'object'},
                    'APIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/APIHostPortsResult'}},
                                     'type': 'object'},
                    'CACert': {'properties': {'Result': {'$ref': '#/definitions/BytesResult'}},
                               'type': 'object'},
                    'EnsureDead': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'Jobs': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/JobsResults'}},
                             'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'ModelUUID': {'properties': {'Result': {'$ref': '#/definitions/StringResult'}},
                                  'type': 'object'},
                    'SetMachineAddresses': {'properties': {'Params': {'$ref': '#/definitions/SetMachinesAddresses'},
                                                           'Result': {'$ref': '#/definitions/ErrorResults'}},
                                            'type': 'object'},
                    'SetObservedNetworkConfig': {'properties': {'Params': {'$ref': '#/definitions/SetMachineNetworkConfig'}},
                                                 'type': 'object'},
                    'SetProviderNetworkConfig': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                 'type': 'object'},
                    'SetStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'UpdateStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'Watch': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                              'type': 'object'},
                    'WatchAPIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                          'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsResult)
    async def APIAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='APIAddresses', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIAddresses)



    #@ReturnMapping(APIHostPortsResult)
    async def APIHostPorts(self):
        '''

        Returns -> typing.Sequence[~HostPort]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='APIHostPorts', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIHostPorts)



    #@ReturnMapping(BytesResult)
    async def CACert(self):
        '''

        Returns -> typing.Sequence[int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='CACert', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CACert)



    #@ReturnMapping(ErrorResults)
    async def EnsureDead(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='EnsureDead', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, EnsureDead)



    #@ReturnMapping(JobsResults)
    async def Jobs(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~JobsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='Jobs', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Jobs)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='Life', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(StringResult)
    async def ModelUUID(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='ModelUUID', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelUUID)



    #@ReturnMapping(ErrorResults)
    async def SetMachineAddresses(self, machineaddresses):
        '''
        machineaddresses : typing.Sequence[~MachineAddresses]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='SetMachineAddresses', Version=1, Params=params)
        params['MachineAddresses'] = machineaddresses
        reply = await self.rpc(msg)
        return self._map(reply, SetMachineAddresses)



    #@ReturnMapping(None)
    async def SetObservedNetworkConfig(self, tag, config):
        '''
        tag : str
        config : typing.Sequence[~NetworkConfig]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='SetObservedNetworkConfig', Version=1, Params=params)
        params['Tag'] = tag
        params['Config'] = config
        reply = await self.rpc(msg)
        return self._map(reply, SetObservedNetworkConfig)



    #@ReturnMapping(ErrorResults)
    async def SetProviderNetworkConfig(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='SetProviderNetworkConfig', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetProviderNetworkConfig)



    #@ReturnMapping(ErrorResults)
    async def SetStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='SetStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetStatus)



    #@ReturnMapping(ErrorResults)
    async def UpdateStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='UpdateStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UpdateStatus)



    #@ReturnMapping(NotifyWatchResults)
    async def Watch(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='Watch', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Watch)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchAPIHostPorts(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Machiner', Request='WatchAPIHostPorts', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAPIHostPorts)


class MeterStatus(Type):
    name = 'MeterStatus'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MeterStatusResult': {'additionalProperties': False,
                                           'properties': {'Code': {'type': 'string'},
                                                          'Error': {'$ref': '#/definitions/Error'},
                                                          'Info': {'type': 'string'}},
                                           'required': ['Code', 'Info', 'Error'],
                                           'type': 'object'},
                     'MeterStatusResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/MeterStatusResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'GetMeterStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/MeterStatusResults'}},
                                       'type': 'object'},
                    'WatchMeterStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                         'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(MeterStatusResults)
    async def GetMeterStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MeterStatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MeterStatus', Request='GetMeterStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetMeterStatus)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchMeterStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MeterStatus', Request='WatchMeterStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchMeterStatus)


class MetricsAdder(Type):
    name = 'MetricsAdder'
    version = 2
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Metric': {'additionalProperties': False,
                                'properties': {'Key': {'type': 'string'},
                                               'Time': {'format': 'date-time',
                                                        'type': 'string'},
                                               'Value': {'type': 'string'}},
                                'required': ['Key', 'Value', 'Time'],
                                'type': 'object'},
                     'MetricBatch': {'additionalProperties': False,
                                     'properties': {'CharmURL': {'type': 'string'},
                                                    'Created': {'format': 'date-time',
                                                                'type': 'string'},
                                                    'Metrics': {'items': {'$ref': '#/definitions/Metric'},
                                                                'type': 'array'},
                                                    'UUID': {'type': 'string'}},
                                     'required': ['UUID',
                                                  'CharmURL',
                                                  'Created',
                                                  'Metrics'],
                                     'type': 'object'},
                     'MetricBatchParam': {'additionalProperties': False,
                                          'properties': {'Batch': {'$ref': '#/definitions/MetricBatch'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag', 'Batch'],
                                          'type': 'object'},
                     'MetricBatchParams': {'additionalProperties': False,
                                           'properties': {'Batches': {'items': {'$ref': '#/definitions/MetricBatchParam'},
                                                                      'type': 'array'}},
                                           'required': ['Batches'],
                                           'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddMetricBatches': {'properties': {'Params': {'$ref': '#/definitions/MetricBatchParams'},
                                                        'Result': {'$ref': '#/definitions/ErrorResults'}},
                                         'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AddMetricBatches(self, batches):
        '''
        batches : typing.Sequence[~MetricBatchParam]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MetricsAdder', Request='AddMetricBatches', Version=2, Params=params)
        params['Batches'] = batches
        reply = await self.rpc(msg)
        return self._map(reply, AddMetricBatches)


class MetricsDebug(Type):
    name = 'MetricsDebug'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityMetrics': {'additionalProperties': False,
                                       'properties': {'error': {'$ref': '#/definitions/Error'},
                                                      'metrics': {'items': {'$ref': '#/definitions/MetricResult'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MeterStatusParam': {'additionalProperties': False,
                                          'properties': {'code': {'type': 'string'},
                                                         'info': {'type': 'string'},
                                                         'tag': {'type': 'string'}},
                                          'required': ['tag', 'code', 'info'],
                                          'type': 'object'},
                     'MeterStatusParams': {'additionalProperties': False,
                                           'properties': {'statues': {'items': {'$ref': '#/definitions/MeterStatusParam'},
                                                                      'type': 'array'}},
                                           'required': ['statues'],
                                           'type': 'object'},
                     'MetricResult': {'additionalProperties': False,
                                      'properties': {'key': {'type': 'string'},
                                                     'time': {'format': 'date-time',
                                                              'type': 'string'},
                                                     'value': {'type': 'string'}},
                                      'required': ['time', 'key', 'value'],
                                      'type': 'object'},
                     'MetricResults': {'additionalProperties': False,
                                       'properties': {'results': {'items': {'$ref': '#/definitions/EntityMetrics'},
                                                                  'type': 'array'}},
                                       'required': ['results'],
                                       'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'GetMetrics': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/MetricResults'}},
                                   'type': 'object'},
                    'SetMeterStatus': {'properties': {'Params': {'$ref': '#/definitions/MeterStatusParams'},
                                                      'Result': {'$ref': '#/definitions/ErrorResults'}},
                                       'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(MetricResults)
    async def GetMetrics(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~EntityMetrics]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MetricsDebug', Request='GetMetrics', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetMetrics)



    #@ReturnMapping(ErrorResults)
    async def SetMeterStatus(self, statues):
        '''
        statues : typing.Sequence[~MeterStatusParam]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MetricsDebug', Request='SetMeterStatus', Version=1, Params=params)
        params['statues'] = statues
        reply = await self.rpc(msg)
        return self._map(reply, SetMeterStatus)


class MetricsManager(Type):
    name = 'MetricsManager'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'CleanupOldMetrics': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'},
                    'SendMetrics': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def CleanupOldMetrics(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MetricsManager', Request='CleanupOldMetrics', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, CleanupOldMetrics)



    #@ReturnMapping(ErrorResults)
    async def SendMetrics(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MetricsManager', Request='SendMetrics', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SendMetrics)


class MigrationFlag(Type):
    name = 'MigrationFlag'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'PhaseResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                    'phase': {'type': 'string'}},
                                     'required': ['phase', 'Error'],
                                     'type': 'object'},
                     'PhaseResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/PhaseResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Phase': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/PhaseResults'}},
                              'type': 'object'},
                    'Watch': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(PhaseResults)
    async def Phase(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~PhaseResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationFlag', Request='Phase', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Phase)



    #@ReturnMapping(NotifyWatchResults)
    async def Watch(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationFlag', Request='Watch', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Watch)


class MigrationMaster(Type):
    name = 'MigrationMaster'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'FullMigrationStatus': {'additionalProperties': False,
                                             'properties': {'attempt': {'type': 'integer'},
                                                            'phase': {'type': 'string'},
                                                            'spec': {'$ref': '#/definitions/ModelMigrationSpec'}},
                                             'required': ['spec',
                                                          'attempt',
                                                          'phase'],
                                             'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ModelMigrationSpec': {'additionalProperties': False,
                                            'properties': {'model-tag': {'type': 'string'},
                                                           'target-info': {'$ref': '#/definitions/ModelMigrationTargetInfo'}},
                                            'required': ['model-tag',
                                                         'target-info'],
                                            'type': 'object'},
                     'ModelMigrationTargetInfo': {'additionalProperties': False,
                                                  'properties': {'addrs': {'items': {'type': 'string'},
                                                                           'type': 'array'},
                                                                 'auth-tag': {'type': 'string'},
                                                                 'ca-cert': {'type': 'string'},
                                                                 'controller-tag': {'type': 'string'},
                                                                 'password': {'type': 'string'}},
                                                  'required': ['controller-tag',
                                                               'addrs',
                                                               'ca-cert',
                                                               'auth-tag',
                                                               'password'],
                                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'SerializedModel': {'additionalProperties': False,
                                         'properties': {'bytes': {'items': {'type': 'integer'},
                                                                  'type': 'array'}},
                                         'required': ['bytes'],
                                         'type': 'object'},
                     'SetMigrationPhaseArgs': {'additionalProperties': False,
                                               'properties': {'phase': {'type': 'string'}},
                                               'required': ['phase'],
                                               'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Export': {'properties': {'Result': {'$ref': '#/definitions/SerializedModel'}},
                               'type': 'object'},
                    'GetMigrationStatus': {'properties': {'Result': {'$ref': '#/definitions/FullMigrationStatus'}},
                                           'type': 'object'},
                    'SetPhase': {'properties': {'Params': {'$ref': '#/definitions/SetMigrationPhaseArgs'}},
                                 'type': 'object'},
                    'Watch': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(SerializedModel)
    async def Export(self):
        '''

        Returns -> typing.Sequence[int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationMaster', Request='Export', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Export)



    #@ReturnMapping(FullMigrationStatus)
    async def GetMigrationStatus(self):
        '''

        Returns -> typing.Union[str, ~ModelMigrationSpec, int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationMaster', Request='GetMigrationStatus', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, GetMigrationStatus)



    #@ReturnMapping(None)
    async def SetPhase(self, phase):
        '''
        phase : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationMaster', Request='SetPhase', Version=1, Params=params)
        params['phase'] = phase
        reply = await self.rpc(msg)
        return self._map(reply, SetPhase)



    #@ReturnMapping(NotifyWatchResult)
    async def Watch(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationMaster', Request='Watch', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Watch)


class MigrationMinion(Type):
    name = 'MigrationMinion'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Watch': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(NotifyWatchResult)
    async def Watch(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationMinion', Request='Watch', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Watch)


class MigrationStatusWatcher(Type):
    name = 'MigrationStatusWatcher'
    version = 1
    schema =     {'definitions': {'MigrationStatus': {'additionalProperties': False,
                                         'properties': {'attempt': {'type': 'integer'},
                                                        'phase': {'type': 'string'},
                                                        'source-api-addrs': {'items': {'type': 'string'},
                                                                             'type': 'array'},
                                                        'source-ca-cert': {'type': 'string'},
                                                        'target-api-addrs': {'items': {'type': 'string'},
                                                                             'type': 'array'},
                                                        'target-ca-cert': {'type': 'string'}},
                                         'required': ['attempt',
                                                      'phase',
                                                      'source-api-addrs',
                                                      'source-ca-cert',
                                                      'target-api-addrs',
                                                      'target-ca-cert'],
                                         'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/MigrationStatus'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(MigrationStatus)
    async def Next(self):
        '''

        Returns -> typing.Union[typing.Sequence[str], int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationStatusWatcher', Request='Next', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationStatusWatcher', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class MigrationTarget(Type):
    name = 'MigrationTarget'
    version = 1
    schema =     {'definitions': {'ModelArgs': {'additionalProperties': False,
                                   'properties': {'model-tag': {'type': 'string'}},
                                   'required': ['model-tag'],
                                   'type': 'object'},
                     'SerializedModel': {'additionalProperties': False,
                                         'properties': {'bytes': {'items': {'type': 'integer'},
                                                                  'type': 'array'}},
                                         'required': ['bytes'],
                                         'type': 'object'}},
     'properties': {'Abort': {'properties': {'Params': {'$ref': '#/definitions/ModelArgs'}},
                              'type': 'object'},
                    'Activate': {'properties': {'Params': {'$ref': '#/definitions/ModelArgs'}},
                                 'type': 'object'},
                    'Import': {'properties': {'Params': {'$ref': '#/definitions/SerializedModel'}},
                               'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(None)
    async def Abort(self, model_tag):
        '''
        model_tag : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationTarget', Request='Abort', Version=1, Params=params)
        params['model-tag'] = model_tag
        reply = await self.rpc(msg)
        return self._map(reply, Abort)



    #@ReturnMapping(None)
    async def Activate(self, model_tag):
        '''
        model_tag : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationTarget', Request='Activate', Version=1, Params=params)
        params['model-tag'] = model_tag
        reply = await self.rpc(msg)
        return self._map(reply, Activate)



    #@ReturnMapping(None)
    async def Import(self, bytes_):
        '''
        bytes_ : typing.Sequence[int]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='MigrationTarget', Request='Import', Version=1, Params=params)
        params['bytes'] = bytes_
        reply = await self.rpc(msg)
        return self._map(reply, Import)


class ModelManager(Type):
    name = 'ModelManager'
    version = 2
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatus': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Info': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Model': {'additionalProperties': False,
                               'properties': {'Name': {'type': 'string'},
                                              'OwnerTag': {'type': 'string'},
                                              'UUID': {'type': 'string'}},
                               'required': ['Name', 'UUID', 'OwnerTag'],
                               'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'ModelCreateArgs': {'additionalProperties': False,
                                         'properties': {'Account': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                 'type': 'object'}},
                                                                    'type': 'object'},
                                                        'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                'type': 'object'}},
                                                                   'type': 'object'},
                                                        'OwnerTag': {'type': 'string'}},
                                         'required': ['OwnerTag',
                                                      'Account',
                                                      'Config'],
                                         'type': 'object'},
                     'ModelInfo': {'additionalProperties': False,
                                   'properties': {'DefaultSeries': {'type': 'string'},
                                                  'Life': {'type': 'string'},
                                                  'Name': {'type': 'string'},
                                                  'OwnerTag': {'type': 'string'},
                                                  'ProviderType': {'type': 'string'},
                                                  'ServerUUID': {'type': 'string'},
                                                  'Status': {'$ref': '#/definitions/EntityStatus'},
                                                  'UUID': {'type': 'string'},
                                                  'Users': {'items': {'$ref': '#/definitions/ModelUserInfo'},
                                                            'type': 'array'}},
                                   'required': ['Name',
                                                'UUID',
                                                'ServerUUID',
                                                'ProviderType',
                                                'DefaultSeries',
                                                'OwnerTag',
                                                'Life',
                                                'Status',
                                                'Users'],
                                   'type': 'object'},
                     'ModelInfoResult': {'additionalProperties': False,
                                         'properties': {'error': {'$ref': '#/definitions/Error'},
                                                        'result': {'$ref': '#/definitions/ModelInfo'}},
                                         'type': 'object'},
                     'ModelInfoResults': {'additionalProperties': False,
                                          'properties': {'results': {'items': {'$ref': '#/definitions/ModelInfoResult'},
                                                                     'type': 'array'}},
                                          'required': ['results'],
                                          'type': 'object'},
                     'ModelSkeletonConfigArgs': {'additionalProperties': False,
                                                 'properties': {'Provider': {'type': 'string'},
                                                                'Region': {'type': 'string'}},
                                                 'required': ['Provider', 'Region'],
                                                 'type': 'object'},
                     'ModelUserInfo': {'additionalProperties': False,
                                       'properties': {'access': {'type': 'string'},
                                                      'displayname': {'type': 'string'},
                                                      'lastconnection': {'format': 'date-time',
                                                                         'type': 'string'},
                                                      'user': {'type': 'string'}},
                                       'required': ['user',
                                                    'displayname',
                                                    'lastconnection',
                                                    'access'],
                                       'type': 'object'},
                     'ModifyModelAccess': {'additionalProperties': False,
                                           'properties': {'access': {'type': 'string'},
                                                          'action': {'type': 'string'},
                                                          'model-tag': {'type': 'string'},
                                                          'user-tag': {'type': 'string'}},
                                           'required': ['user-tag',
                                                        'action',
                                                        'access',
                                                        'model-tag'],
                                           'type': 'object'},
                     'ModifyModelAccessRequest': {'additionalProperties': False,
                                                  'properties': {'changes': {'items': {'$ref': '#/definitions/ModifyModelAccess'},
                                                                             'type': 'array'}},
                                                  'required': ['changes'],
                                                  'type': 'object'},
                     'UserModel': {'additionalProperties': False,
                                   'properties': {'LastConnection': {'format': 'date-time',
                                                                     'type': 'string'},
                                                  'Model': {'$ref': '#/definitions/Model'}},
                                   'required': ['Model', 'LastConnection'],
                                   'type': 'object'},
                     'UserModelList': {'additionalProperties': False,
                                       'properties': {'UserModels': {'items': {'$ref': '#/definitions/UserModel'},
                                                                     'type': 'array'}},
                                       'required': ['UserModels'],
                                       'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ConfigSkeleton': {'properties': {'Params': {'$ref': '#/definitions/ModelSkeletonConfigArgs'},
                                                      'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                       'type': 'object'},
                    'CreateModel': {'properties': {'Params': {'$ref': '#/definitions/ModelCreateArgs'},
                                                   'Result': {'$ref': '#/definitions/Model'}},
                                    'type': 'object'},
                    'ListModels': {'properties': {'Params': {'$ref': '#/definitions/Entity'},
                                                  'Result': {'$ref': '#/definitions/UserModelList'}},
                                   'type': 'object'},
                    'ModelInfo': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                 'Result': {'$ref': '#/definitions/ModelInfoResults'}},
                                  'type': 'object'},
                    'ModifyModelAccess': {'properties': {'Params': {'$ref': '#/definitions/ModifyModelAccessRequest'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ModelConfigResult)
    async def ConfigSkeleton(self, region, provider):
        '''
        region : str
        provider : str
        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ModelManager', Request='ConfigSkeleton', Version=2, Params=params)
        params['Region'] = region
        params['Provider'] = provider
        reply = await self.rpc(msg)
        return self._map(reply, ConfigSkeleton)



    #@ReturnMapping(Model)
    async def CreateModel(self, account, ownertag, config):
        '''
        account : typing.Mapping[str, typing.Any]
        ownertag : str
        config : typing.Mapping[str, typing.Any]
        Returns -> <class 'str'>
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ModelManager', Request='CreateModel', Version=2, Params=params)
        params['Account'] = account
        params['OwnerTag'] = ownertag
        params['Config'] = config
        reply = await self.rpc(msg)
        return self._map(reply, CreateModel)



    #@ReturnMapping(UserModelList)
    async def ListModels(self, tag):
        '''
        tag : str
        Returns -> typing.Sequence[~UserModel]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ModelManager', Request='ListModels', Version=2, Params=params)
        params['Tag'] = tag
        reply = await self.rpc(msg)
        return self._map(reply, ListModels)



    #@ReturnMapping(ModelInfoResults)
    async def ModelInfo(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ModelInfoResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ModelManager', Request='ModelInfo', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ModelInfo)



    #@ReturnMapping(ErrorResults)
    async def ModifyModelAccess(self, changes):
        '''
        changes : typing.Sequence[~ModifyModelAccess]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ModelManager', Request='ModifyModelAccess', Version=2, Params=params)
        params['changes'] = changes
        reply = await self.rpc(msg)
        return self._map(reply, ModifyModelAccess)


class NotifyWatcher(Type):
    name = 'NotifyWatcher'
    version = 1
    schema =     {'properties': {'Next': {'type': 'object'}, 'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(None)
    async def Next(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='NotifyWatcher', Request='Next', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='NotifyWatcher', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Pinger(Type):
    name = 'Pinger'
    version = 1
    schema =     {'properties': {'Ping': {'type': 'object'}, 'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(None)
    async def Ping(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Pinger', Request='Ping', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Ping)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Pinger', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Provisioner(Type):
    name = 'Provisioner'
    version = 2
    schema =     {'definitions': {'APIHostPortsResult': {'additionalProperties': False,
                                            'properties': {'Servers': {'items': {'items': {'$ref': '#/definitions/HostPort'},
                                                                                 'type': 'array'},
                                                                       'type': 'array'}},
                                            'required': ['Servers'],
                                            'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'Binary': {'additionalProperties': False,
                                'properties': {'Arch': {'type': 'string'},
                                               'Number': {'$ref': '#/definitions/Number'},
                                               'Series': {'type': 'string'}},
                                'required': ['Number', 'Series', 'Arch'],
                                'type': 'object'},
                     'BytesResult': {'additionalProperties': False,
                                     'properties': {'Result': {'items': {'type': 'integer'},
                                                               'type': 'array'}},
                                     'required': ['Result'],
                                     'type': 'object'},
                     'CloudImageMetadata': {'additionalProperties': False,
                                            'properties': {'arch': {'type': 'string'},
                                                           'image_id': {'type': 'string'},
                                                           'priority': {'type': 'integer'},
                                                           'region': {'type': 'string'},
                                                           'root_storage_size': {'type': 'integer'},
                                                           'root_storage_type': {'type': 'string'},
                                                           'series': {'type': 'string'},
                                                           'source': {'type': 'string'},
                                                           'stream': {'type': 'string'},
                                                           'version': {'type': 'string'},
                                                           'virt_type': {'type': 'string'}},
                                            'required': ['image_id',
                                                         'region',
                                                         'version',
                                                         'series',
                                                         'arch',
                                                         'source',
                                                         'priority'],
                                            'type': 'object'},
                     'ConstraintsResult': {'additionalProperties': False,
                                           'properties': {'Constraints': {'$ref': '#/definitions/Value'},
                                                          'Error': {'$ref': '#/definitions/Error'}},
                                           'required': ['Error', 'Constraints'],
                                           'type': 'object'},
                     'ConstraintsResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/ConstraintsResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'ContainerConfig': {'additionalProperties': False,
                                         'properties': {'AllowLXCLoopMounts': {'type': 'boolean'},
                                                        'AptMirror': {'type': 'string'},
                                                        'AptProxy': {'$ref': '#/definitions/Settings'},
                                                        'AuthorizedKeys': {'type': 'string'},
                                                        'PreferIPv6': {'type': 'boolean'},
                                                        'ProviderType': {'type': 'string'},
                                                        'Proxy': {'$ref': '#/definitions/Settings'},
                                                        'SSLHostnameVerification': {'type': 'boolean'},
                                                        'UpdateBehavior': {'$ref': '#/definitions/UpdateBehavior'}},
                                         'required': ['ProviderType',
                                                      'AuthorizedKeys',
                                                      'SSLHostnameVerification',
                                                      'Proxy',
                                                      'AptProxy',
                                                      'AptMirror',
                                                      'PreferIPv6',
                                                      'AllowLXCLoopMounts',
                                                      'UpdateBehavior'],
                                         'type': 'object'},
                     'ContainerManagerConfig': {'additionalProperties': False,
                                                'properties': {'ManagerConfig': {'patternProperties': {'.*': {'type': 'string'}},
                                                                                 'type': 'object'}},
                                                'required': ['ManagerConfig'],
                                                'type': 'object'},
                     'ContainerManagerConfigParams': {'additionalProperties': False,
                                                      'properties': {'Type': {'type': 'string'}},
                                                      'required': ['Type'],
                                                      'type': 'object'},
                     'DistributionGroupResult': {'additionalProperties': False,
                                                 'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                'Result': {'items': {'type': 'string'},
                                                                           'type': 'array'}},
                                                 'required': ['Error', 'Result'],
                                                 'type': 'object'},
                     'DistributionGroupResults': {'additionalProperties': False,
                                                  'properties': {'Results': {'items': {'$ref': '#/definitions/DistributionGroupResult'},
                                                                             'type': 'array'}},
                                                  'required': ['Results'],
                                                  'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityPassword': {'additionalProperties': False,
                                        'properties': {'Password': {'type': 'string'},
                                                       'Tag': {'type': 'string'}},
                                        'required': ['Tag', 'Password'],
                                        'type': 'object'},
                     'EntityPasswords': {'additionalProperties': False,
                                         'properties': {'Changes': {'items': {'$ref': '#/definitions/EntityPassword'},
                                                                    'type': 'array'}},
                                         'required': ['Changes'],
                                         'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'FindToolsParams': {'additionalProperties': False,
                                         'properties': {'Arch': {'type': 'string'},
                                                        'MajorVersion': {'type': 'integer'},
                                                        'MinorVersion': {'type': 'integer'},
                                                        'Number': {'$ref': '#/definitions/Number'},
                                                        'Series': {'type': 'string'}},
                                         'required': ['Number',
                                                      'MajorVersion',
                                                      'MinorVersion',
                                                      'Arch',
                                                      'Series'],
                                         'type': 'object'},
                     'FindToolsResult': {'additionalProperties': False,
                                         'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                        'List': {'items': {'$ref': '#/definitions/Tools'},
                                                                 'type': 'array'}},
                                         'required': ['List', 'Error'],
                                         'type': 'object'},
                     'HardwareCharacteristics': {'additionalProperties': False,
                                                 'properties': {'Arch': {'type': 'string'},
                                                                'AvailabilityZone': {'type': 'string'},
                                                                'CpuCores': {'type': 'integer'},
                                                                'CpuPower': {'type': 'integer'},
                                                                'Mem': {'type': 'integer'},
                                                                'RootDisk': {'type': 'integer'},
                                                                'Tags': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                                 'type': 'object'},
                     'HostPort': {'additionalProperties': False,
                                  'properties': {'Address': {'$ref': '#/definitions/Address'},
                                                 'Port': {'type': 'integer'}},
                                  'required': ['Address', 'Port'],
                                  'type': 'object'},
                     'InstanceInfo': {'additionalProperties': False,
                                      'properties': {'Characteristics': {'$ref': '#/definitions/HardwareCharacteristics'},
                                                     'InstanceId': {'type': 'string'},
                                                     'NetworkConfig': {'items': {'$ref': '#/definitions/NetworkConfig'},
                                                                       'type': 'array'},
                                                     'Nonce': {'type': 'string'},
                                                     'Tag': {'type': 'string'},
                                                     'VolumeAttachments': {'patternProperties': {'.*': {'$ref': '#/definitions/VolumeAttachmentInfo'}},
                                                                           'type': 'object'},
                                                     'Volumes': {'items': {'$ref': '#/definitions/Volume'},
                                                                 'type': 'array'}},
                                      'required': ['Tag',
                                                   'InstanceId',
                                                   'Nonce',
                                                   'Characteristics',
                                                   'Volumes',
                                                   'VolumeAttachments',
                                                   'NetworkConfig'],
                                      'type': 'object'},
                     'InstancesInfo': {'additionalProperties': False,
                                       'properties': {'Machines': {'items': {'$ref': '#/definitions/InstanceInfo'},
                                                                   'type': 'array'}},
                                       'required': ['Machines'],
                                       'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineContainers': {'additionalProperties': False,
                                           'properties': {'ContainerTypes': {'items': {'type': 'string'},
                                                                             'type': 'array'},
                                                          'MachineTag': {'type': 'string'}},
                                           'required': ['MachineTag',
                                                        'ContainerTypes'],
                                           'type': 'object'},
                     'MachineContainersParams': {'additionalProperties': False,
                                                 'properties': {'Params': {'items': {'$ref': '#/definitions/MachineContainers'},
                                                                           'type': 'array'}},
                                                 'required': ['Params'],
                                                 'type': 'object'},
                     'MachineNetworkConfigResult': {'additionalProperties': False,
                                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                   'Info': {'items': {'$ref': '#/definitions/NetworkConfig'},
                                                                            'type': 'array'}},
                                                    'required': ['Error', 'Info'],
                                                    'type': 'object'},
                     'MachineNetworkConfigResults': {'additionalProperties': False,
                                                     'properties': {'Results': {'items': {'$ref': '#/definitions/MachineNetworkConfigResult'},
                                                                                'type': 'array'}},
                                                     'required': ['Results'],
                                                     'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NetworkConfig': {'additionalProperties': False,
                                       'properties': {'Address': {'type': 'string'},
                                                      'CIDR': {'type': 'string'},
                                                      'ConfigType': {'type': 'string'},
                                                      'DNSSearchDomains': {'items': {'type': 'string'},
                                                                           'type': 'array'},
                                                      'DNSServers': {'items': {'type': 'string'},
                                                                     'type': 'array'},
                                                      'DeviceIndex': {'type': 'integer'},
                                                      'Disabled': {'type': 'boolean'},
                                                      'GatewayAddress': {'type': 'string'},
                                                      'InterfaceName': {'type': 'string'},
                                                      'InterfaceType': {'type': 'string'},
                                                      'MACAddress': {'type': 'string'},
                                                      'MTU': {'type': 'integer'},
                                                      'NoAutoStart': {'type': 'boolean'},
                                                      'ParentInterfaceName': {'type': 'string'},
                                                      'ProviderAddressId': {'type': 'string'},
                                                      'ProviderId': {'type': 'string'},
                                                      'ProviderSpaceId': {'type': 'string'},
                                                      'ProviderSubnetId': {'type': 'string'},
                                                      'ProviderVLANId': {'type': 'string'},
                                                      'VLANTag': {'type': 'integer'}},
                                       'required': ['DeviceIndex',
                                                    'MACAddress',
                                                    'CIDR',
                                                    'MTU',
                                                    'ProviderId',
                                                    'ProviderSubnetId',
                                                    'ProviderSpaceId',
                                                    'ProviderAddressId',
                                                    'ProviderVLANId',
                                                    'VLANTag',
                                                    'InterfaceName',
                                                    'ParentInterfaceName',
                                                    'InterfaceType',
                                                    'Disabled'],
                                       'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'Number': {'additionalProperties': False,
                                'properties': {'Build': {'type': 'integer'},
                                               'Major': {'type': 'integer'},
                                               'Minor': {'type': 'integer'},
                                               'Patch': {'type': 'integer'},
                                               'Tag': {'type': 'string'}},
                                'required': ['Major',
                                             'Minor',
                                             'Tag',
                                             'Patch',
                                             'Build'],
                                'type': 'object'},
                     'ProvisioningInfo': {'additionalProperties': False,
                                          'properties': {'Constraints': {'$ref': '#/definitions/Value'},
                                                         'EndpointBindings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                              'type': 'object'},
                                                         'ImageMetadata': {'items': {'$ref': '#/definitions/CloudImageMetadata'},
                                                                           'type': 'array'},
                                                         'Jobs': {'items': {'type': 'string'},
                                                                  'type': 'array'},
                                                         'Placement': {'type': 'string'},
                                                         'Series': {'type': 'string'},
                                                         'SubnetsToZones': {'patternProperties': {'.*': {'items': {'type': 'string'},
                                                                                                         'type': 'array'}},
                                                                            'type': 'object'},
                                                         'Tags': {'patternProperties': {'.*': {'type': 'string'}},
                                                                  'type': 'object'},
                                                         'Volumes': {'items': {'$ref': '#/definitions/VolumeParams'},
                                                                     'type': 'array'}},
                                          'required': ['Constraints',
                                                       'Series',
                                                       'Placement',
                                                       'Jobs',
                                                       'Volumes',
                                                       'Tags',
                                                       'SubnetsToZones',
                                                       'ImageMetadata',
                                                       'EndpointBindings'],
                                          'type': 'object'},
                     'ProvisioningInfoResult': {'additionalProperties': False,
                                                'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                               'Result': {'$ref': '#/definitions/ProvisioningInfo'}},
                                                'required': ['Error', 'Result'],
                                                'type': 'object'},
                     'ProvisioningInfoResults': {'additionalProperties': False,
                                                 'properties': {'Results': {'items': {'$ref': '#/definitions/ProvisioningInfoResult'},
                                                                            'type': 'array'}},
                                                 'required': ['Results'],
                                                 'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'Settings': {'additionalProperties': False,
                                  'properties': {'Ftp': {'type': 'string'},
                                                 'Http': {'type': 'string'},
                                                 'Https': {'type': 'string'},
                                                 'NoProxy': {'type': 'string'}},
                                  'required': ['Http', 'Https', 'Ftp', 'NoProxy'],
                                  'type': 'object'},
                     'StatusResult': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Error': {'$ref': '#/definitions/Error'},
                                                     'Id': {'type': 'string'},
                                                     'Info': {'type': 'string'},
                                                     'Life': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Error',
                                                   'Id',
                                                   'Life',
                                                   'Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'StatusResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StatusResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'Tools': {'additionalProperties': False,
                               'properties': {'sha256': {'type': 'string'},
                                              'size': {'type': 'integer'},
                                              'url': {'type': 'string'},
                                              'version': {'$ref': '#/definitions/Binary'}},
                               'required': ['version', 'url', 'size'],
                               'type': 'object'},
                     'ToolsResult': {'additionalProperties': False,
                                     'properties': {'DisableSSLHostnameVerification': {'type': 'boolean'},
                                                    'Error': {'$ref': '#/definitions/Error'},
                                                    'ToolsList': {'items': {'$ref': '#/definitions/Tools'},
                                                                  'type': 'array'}},
                                     'required': ['ToolsList',
                                                  'DisableSSLHostnameVerification',
                                                  'Error'],
                                     'type': 'object'},
                     'ToolsResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ToolsResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'UpdateBehavior': {'additionalProperties': False,
                                        'properties': {'EnableOSRefreshUpdate': {'type': 'boolean'},
                                                       'EnableOSUpgrade': {'type': 'boolean'}},
                                        'required': ['EnableOSRefreshUpdate',
                                                     'EnableOSUpgrade'],
                                        'type': 'object'},
                     'Value': {'additionalProperties': False,
                               'properties': {'arch': {'type': 'string'},
                                              'container': {'type': 'string'},
                                              'cpu-cores': {'type': 'integer'},
                                              'cpu-power': {'type': 'integer'},
                                              'instance-type': {'type': 'string'},
                                              'mem': {'type': 'integer'},
                                              'root-disk': {'type': 'integer'},
                                              'spaces': {'items': {'type': 'string'},
                                                         'type': 'array'},
                                              'tags': {'items': {'type': 'string'},
                                                       'type': 'array'},
                                              'virt-type': {'type': 'string'}},
                               'type': 'object'},
                     'Volume': {'additionalProperties': False,
                                'properties': {'info': {'$ref': '#/definitions/VolumeInfo'},
                                               'volumetag': {'type': 'string'}},
                                'required': ['volumetag', 'info'],
                                'type': 'object'},
                     'VolumeAttachmentInfo': {'additionalProperties': False,
                                              'properties': {'busaddress': {'type': 'string'},
                                                             'devicelink': {'type': 'string'},
                                                             'devicename': {'type': 'string'},
                                                             'read-only': {'type': 'boolean'}},
                                              'type': 'object'},
                     'VolumeAttachmentParams': {'additionalProperties': False,
                                                'properties': {'instanceid': {'type': 'string'},
                                                               'machinetag': {'type': 'string'},
                                                               'provider': {'type': 'string'},
                                                               'read-only': {'type': 'boolean'},
                                                               'volumeid': {'type': 'string'},
                                                               'volumetag': {'type': 'string'}},
                                                'required': ['volumetag',
                                                             'machinetag',
                                                             'provider'],
                                                'type': 'object'},
                     'VolumeInfo': {'additionalProperties': False,
                                    'properties': {'hardwareid': {'type': 'string'},
                                                   'persistent': {'type': 'boolean'},
                                                   'size': {'type': 'integer'},
                                                   'volumeid': {'type': 'string'}},
                                    'required': ['volumeid', 'size', 'persistent'],
                                    'type': 'object'},
                     'VolumeParams': {'additionalProperties': False,
                                      'properties': {'attachment': {'$ref': '#/definitions/VolumeAttachmentParams'},
                                                     'attributes': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                 'type': 'object'}},
                                                                    'type': 'object'},
                                                     'provider': {'type': 'string'},
                                                     'size': {'type': 'integer'},
                                                     'tags': {'patternProperties': {'.*': {'type': 'string'}},
                                                              'type': 'object'},
                                                     'volumetag': {'type': 'string'}},
                                      'required': ['volumetag', 'size', 'provider'],
                                      'type': 'object'},
                     'WatchContainer': {'additionalProperties': False,
                                        'properties': {'ContainerType': {'type': 'string'},
                                                       'MachineTag': {'type': 'string'}},
                                        'required': ['MachineTag', 'ContainerType'],
                                        'type': 'object'},
                     'WatchContainers': {'additionalProperties': False,
                                         'properties': {'Params': {'items': {'$ref': '#/definitions/WatchContainer'},
                                                                   'type': 'array'}},
                                         'required': ['Params'],
                                         'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'APIAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                     'type': 'object'},
                    'APIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/APIHostPortsResult'}},
                                     'type': 'object'},
                    'CACert': {'properties': {'Result': {'$ref': '#/definitions/BytesResult'}},
                               'type': 'object'},
                    'Constraints': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ConstraintsResults'}},
                                    'type': 'object'},
                    'ContainerConfig': {'properties': {'Result': {'$ref': '#/definitions/ContainerConfig'}},
                                        'type': 'object'},
                    'ContainerManagerConfig': {'properties': {'Params': {'$ref': '#/definitions/ContainerManagerConfigParams'},
                                                              'Result': {'$ref': '#/definitions/ContainerManagerConfig'}},
                                               'type': 'object'},
                    'DistributionGroup': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                         'Result': {'$ref': '#/definitions/DistributionGroupResults'}},
                                          'type': 'object'},
                    'EnsureDead': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'FindTools': {'properties': {'Params': {'$ref': '#/definitions/FindToolsParams'},
                                                 'Result': {'$ref': '#/definitions/FindToolsResult'}},
                                  'type': 'object'},
                    'GetContainerInterfaceInfo': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                 'Result': {'$ref': '#/definitions/MachineNetworkConfigResults'}},
                                                  'type': 'object'},
                    'InstanceId': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringResults'}},
                                   'type': 'object'},
                    'InstanceStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/StatusResults'}},
                                       'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'MachinesWithTransientErrors': {'properties': {'Result': {'$ref': '#/definitions/StatusResults'}},
                                                    'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'ModelUUID': {'properties': {'Result': {'$ref': '#/definitions/StringResult'}},
                                  'type': 'object'},
                    'PrepareContainerInterfaceInfo': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                     'Result': {'$ref': '#/definitions/MachineNetworkConfigResults'}},
                                                      'type': 'object'},
                    'ProvisioningInfo': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/ProvisioningInfoResults'}},
                                         'type': 'object'},
                    'ReleaseContainerAddresses': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                  'type': 'object'},
                    'Remove': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                               'type': 'object'},
                    'Series': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/StringResults'}},
                               'type': 'object'},
                    'SetInstanceInfo': {'properties': {'Params': {'$ref': '#/definitions/InstancesInfo'},
                                                       'Result': {'$ref': '#/definitions/ErrorResults'}},
                                        'type': 'object'},
                    'SetInstanceStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'},
                    'SetPasswords': {'properties': {'Params': {'$ref': '#/definitions/EntityPasswords'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'SetStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'SetSupportedContainers': {'properties': {'Params': {'$ref': '#/definitions/MachineContainersParams'},
                                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                                               'type': 'object'},
                    'StateAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                       'type': 'object'},
                    'Status': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/StatusResults'}},
                               'type': 'object'},
                    'Tools': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/ToolsResults'}},
                              'type': 'object'},
                    'UpdateStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'WatchAPIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                          'type': 'object'},
                    'WatchAllContainers': {'properties': {'Params': {'$ref': '#/definitions/WatchContainers'},
                                                          'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                           'type': 'object'},
                    'WatchContainers': {'properties': {'Params': {'$ref': '#/definitions/WatchContainers'},
                                                       'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                        'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'},
                    'WatchMachineErrorRetry': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                               'type': 'object'},
                    'WatchModelMachines': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                                           'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsResult)
    async def APIAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='APIAddresses', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIAddresses)



    #@ReturnMapping(APIHostPortsResult)
    async def APIHostPorts(self):
        '''

        Returns -> typing.Sequence[~HostPort]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='APIHostPorts', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIHostPorts)



    #@ReturnMapping(BytesResult)
    async def CACert(self):
        '''

        Returns -> typing.Sequence[int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='CACert', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CACert)



    #@ReturnMapping(ConstraintsResults)
    async def Constraints(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ConstraintsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Constraints', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Constraints)



    #@ReturnMapping(ContainerConfig)
    async def ContainerConfig(self):
        '''

        Returns -> typing.Union[str, bool, ~Settings, ~UpdateBehavior]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ContainerConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ContainerConfig)



    #@ReturnMapping(ContainerManagerConfig)
    async def ContainerManagerConfig(self, type_):
        '''
        type_ : str
        Returns -> typing.Mapping[str, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ContainerManagerConfig', Version=2, Params=params)
        params['Type'] = type_
        reply = await self.rpc(msg)
        return self._map(reply, ContainerManagerConfig)



    #@ReturnMapping(DistributionGroupResults)
    async def DistributionGroup(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~DistributionGroupResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='DistributionGroup', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, DistributionGroup)



    #@ReturnMapping(ErrorResults)
    async def EnsureDead(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='EnsureDead', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, EnsureDead)



    #@ReturnMapping(FindToolsResult)
    async def FindTools(self, majorversion, series, minorversion, arch, number):
        '''
        majorversion : int
        series : str
        minorversion : int
        arch : str
        number : ~Number
        Returns -> typing.Union[~Error, typing.Sequence[~Tools]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='FindTools', Version=2, Params=params)
        params['MajorVersion'] = majorversion
        params['Series'] = series
        params['MinorVersion'] = minorversion
        params['Arch'] = arch
        params['Number'] = number
        reply = await self.rpc(msg)
        return self._map(reply, FindTools)



    #@ReturnMapping(MachineNetworkConfigResults)
    async def GetContainerInterfaceInfo(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachineNetworkConfigResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='GetContainerInterfaceInfo', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetContainerInterfaceInfo)



    #@ReturnMapping(StringResults)
    async def InstanceId(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='InstanceId', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceId)



    #@ReturnMapping(StatusResults)
    async def InstanceStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='InstanceStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceStatus)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Life', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(StatusResults)
    async def MachinesWithTransientErrors(self):
        '''

        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='MachinesWithTransientErrors', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, MachinesWithTransientErrors)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(StringResult)
    async def ModelUUID(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ModelUUID', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelUUID)



    #@ReturnMapping(MachineNetworkConfigResults)
    async def PrepareContainerInterfaceInfo(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachineNetworkConfigResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='PrepareContainerInterfaceInfo', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PrepareContainerInterfaceInfo)



    #@ReturnMapping(ProvisioningInfoResults)
    async def ProvisioningInfo(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ProvisioningInfoResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ProvisioningInfo', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ProvisioningInfo)



    #@ReturnMapping(ErrorResults)
    async def ReleaseContainerAddresses(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='ReleaseContainerAddresses', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ReleaseContainerAddresses)



    #@ReturnMapping(ErrorResults)
    async def Remove(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Remove', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Remove)



    #@ReturnMapping(StringResults)
    async def Series(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Series', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Series)



    #@ReturnMapping(ErrorResults)
    async def SetInstanceInfo(self, machines):
        '''
        machines : typing.Sequence[~InstanceInfo]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='SetInstanceInfo', Version=2, Params=params)
        params['Machines'] = machines
        reply = await self.rpc(msg)
        return self._map(reply, SetInstanceInfo)



    #@ReturnMapping(ErrorResults)
    async def SetInstanceStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='SetInstanceStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetInstanceStatus)



    #@ReturnMapping(ErrorResults)
    async def SetPasswords(self, changes):
        '''
        changes : typing.Sequence[~EntityPassword]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='SetPasswords', Version=2, Params=params)
        params['Changes'] = changes
        reply = await self.rpc(msg)
        return self._map(reply, SetPasswords)



    #@ReturnMapping(ErrorResults)
    async def SetStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='SetStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetStatus)



    #@ReturnMapping(ErrorResults)
    async def SetSupportedContainers(self, params):
        '''
        params : typing.Sequence[~MachineContainers]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='SetSupportedContainers', Version=2, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, SetSupportedContainers)



    #@ReturnMapping(StringsResult)
    async def StateAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='StateAddresses', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, StateAddresses)



    #@ReturnMapping(StatusResults)
    async def Status(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Status', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Status)



    #@ReturnMapping(ToolsResults)
    async def Tools(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ToolsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='Tools', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Tools)



    #@ReturnMapping(ErrorResults)
    async def UpdateStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='UpdateStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UpdateStatus)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchAPIHostPorts(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchAPIHostPorts', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAPIHostPorts)



    #@ReturnMapping(StringsWatchResults)
    async def WatchAllContainers(self, params):
        '''
        params : typing.Sequence[~WatchContainer]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchAllContainers', Version=2, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, WatchAllContainers)



    #@ReturnMapping(StringsWatchResults)
    async def WatchContainers(self, params):
        '''
        params : typing.Sequence[~WatchContainer]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchContainers', Version=2, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, WatchContainers)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchForModelConfigChanges', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchMachineErrorRetry(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchMachineErrorRetry', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchMachineErrorRetry)



    #@ReturnMapping(StringsWatchResult)
    async def WatchModelMachines(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Provisioner', Request='WatchModelMachines', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchModelMachines)


class ProxyUpdater(Type):
    name = 'ProxyUpdater'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'ProxyConfig': {'additionalProperties': False,
                                     'properties': {'FTP': {'type': 'string'},
                                                    'HTTP': {'type': 'string'},
                                                    'HTTPS': {'type': 'string'},
                                                    'NoProxy': {'type': 'string'}},
                                     'required': ['HTTP',
                                                  'HTTPS',
                                                  'FTP',
                                                  'NoProxy'],
                                     'type': 'object'},
                     'ProxyConfigResult': {'additionalProperties': False,
                                           'properties': {'APTProxySettings': {'$ref': '#/definitions/ProxyConfig'},
                                                          'Error': {'$ref': '#/definitions/Error'},
                                                          'ProxySettings': {'$ref': '#/definitions/ProxyConfig'}},
                                           'required': ['ProxySettings',
                                                        'APTProxySettings'],
                                           'type': 'object'},
                     'ProxyConfigResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/ProxyConfigResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ProxyConfig': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ProxyConfigResults'}},
                                    'type': 'object'},
                    'WatchForProxyConfigAndAPIHostPortChanges': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                                'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                                                 'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ProxyConfigResults)
    async def ProxyConfig(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ProxyConfigResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ProxyUpdater', Request='ProxyConfig', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ProxyConfig)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchForProxyConfigAndAPIHostPortChanges(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ProxyUpdater', Request='WatchForProxyConfigAndAPIHostPortChanges', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchForProxyConfigAndAPIHostPortChanges)


class Reboot(Type):
    name = 'Reboot'
    version = 2
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'RebootActionResult': {'additionalProperties': False,
                                            'properties': {'error': {'$ref': '#/definitions/Error'},
                                                           'result': {'type': 'string'}},
                                            'type': 'object'},
                     'RebootActionResults': {'additionalProperties': False,
                                             'properties': {'results': {'items': {'$ref': '#/definitions/RebootActionResult'},
                                                                        'type': 'array'}},
                                             'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ClearReboot': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'GetRebootAction': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/RebootActionResults'}},
                                        'type': 'object'},
                    'RequestReboot': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'WatchForRebootEvent': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                            'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def ClearReboot(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Reboot', Request='ClearReboot', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ClearReboot)



    #@ReturnMapping(RebootActionResults)
    async def GetRebootAction(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~RebootActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Reboot', Request='GetRebootAction', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetRebootAction)



    #@ReturnMapping(ErrorResults)
    async def RequestReboot(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Reboot', Request='RequestReboot', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, RequestReboot)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForRebootEvent(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Reboot', Request='WatchForRebootEvent', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForRebootEvent)


class RelationUnitsWatcher(Type):
    name = 'RelationUnitsWatcher'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'RelationUnitsChange': {'additionalProperties': False,
                                             'properties': {'Changed': {'patternProperties': {'.*': {'$ref': '#/definitions/UnitSettings'}},
                                                                        'type': 'object'},
                                                            'Departed': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                             'required': ['Changed', 'Departed'],
                                             'type': 'object'},
                     'RelationUnitsWatchResult': {'additionalProperties': False,
                                                  'properties': {'Changes': {'$ref': '#/definitions/RelationUnitsChange'},
                                                                 'Error': {'$ref': '#/definitions/Error'},
                                                                 'RelationUnitsWatcherId': {'type': 'string'}},
                                                  'required': ['RelationUnitsWatcherId',
                                                               'Changes',
                                                               'Error'],
                                                  'type': 'object'},
                     'UnitSettings': {'additionalProperties': False,
                                      'properties': {'Version': {'type': 'integer'}},
                                      'required': ['Version'],
                                      'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/RelationUnitsWatchResult'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(RelationUnitsWatchResult)
    async def Next(self):
        '''

        Returns -> typing.Union[~Error, str, ~RelationUnitsChange]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='RelationUnitsWatcher', Request='Next', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='RelationUnitsWatcher', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Resumer(Type):
    name = 'Resumer'
    version = 2
    schema =     {'properties': {'ResumeTransactions': {'type': 'object'}}, 'type': 'object'}
    

    #@ReturnMapping(None)
    async def ResumeTransactions(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Resumer', Request='ResumeTransactions', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ResumeTransactions)


class RetryStrategy(Type):
    name = 'RetryStrategy'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'RetryStrategy': {'additionalProperties': False,
                                       'properties': {'JitterRetryTime': {'type': 'boolean'},
                                                      'MaxRetryTime': {'type': 'integer'},
                                                      'MinRetryTime': {'type': 'integer'},
                                                      'RetryTimeFactor': {'type': 'integer'},
                                                      'ShouldRetry': {'type': 'boolean'}},
                                       'required': ['ShouldRetry',
                                                    'MinRetryTime',
                                                    'MaxRetryTime',
                                                    'JitterRetryTime',
                                                    'RetryTimeFactor'],
                                       'type': 'object'},
                     'RetryStrategyResult': {'additionalProperties': False,
                                             'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                            'Result': {'$ref': '#/definitions/RetryStrategy'}},
                                             'required': ['Error', 'Result'],
                                             'type': 'object'},
                     'RetryStrategyResults': {'additionalProperties': False,
                                              'properties': {'Results': {'items': {'$ref': '#/definitions/RetryStrategyResult'},
                                                                         'type': 'array'}},
                                              'required': ['Results'],
                                              'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'RetryStrategy': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/RetryStrategyResults'}},
                                      'type': 'object'},
                    'WatchRetryStrategy': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                          'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                           'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(RetryStrategyResults)
    async def RetryStrategy(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~RetryStrategyResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='RetryStrategy', Request='RetryStrategy', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, RetryStrategy)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchRetryStrategy(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='RetryStrategy', Request='WatchRetryStrategy', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchRetryStrategy)


class SSHClient(Type):
    name = 'SSHClient'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'SSHAddressResult': {'additionalProperties': False,
                                          'properties': {'address': {'type': 'string'},
                                                         'error': {'$ref': '#/definitions/Error'}},
                                          'type': 'object'},
                     'SSHAddressResults': {'additionalProperties': False,
                                           'properties': {'results': {'items': {'$ref': '#/definitions/SSHAddressResult'},
                                                                      'type': 'array'}},
                                           'required': ['results'],
                                           'type': 'object'},
                     'SSHProxyResult': {'additionalProperties': False,
                                        'properties': {'use-proxy': {'type': 'boolean'}},
                                        'required': ['use-proxy'],
                                        'type': 'object'},
                     'SSHPublicKeysResult': {'additionalProperties': False,
                                             'properties': {'error': {'$ref': '#/definitions/Error'},
                                                            'public-keys': {'items': {'type': 'string'},
                                                                            'type': 'array'}},
                                             'type': 'object'},
                     'SSHPublicKeysResults': {'additionalProperties': False,
                                              'properties': {'results': {'items': {'$ref': '#/definitions/SSHPublicKeysResult'},
                                                                         'type': 'array'}},
                                              'required': ['results'],
                                              'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'PrivateAddress': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/SSHAddressResults'}},
                                       'type': 'object'},
                    'Proxy': {'properties': {'Result': {'$ref': '#/definitions/SSHProxyResult'}},
                              'type': 'object'},
                    'PublicAddress': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/SSHAddressResults'}},
                                      'type': 'object'},
                    'PublicKeys': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/SSHPublicKeysResults'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(SSHAddressResults)
    async def PrivateAddress(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~SSHAddressResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='SSHClient', Request='PrivateAddress', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PrivateAddress)



    #@ReturnMapping(SSHProxyResult)
    async def Proxy(self):
        '''

        Returns -> bool
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='SSHClient', Request='Proxy', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Proxy)



    #@ReturnMapping(SSHAddressResults)
    async def PublicAddress(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~SSHAddressResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='SSHClient', Request='PublicAddress', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PublicAddress)



    #@ReturnMapping(SSHPublicKeysResults)
    async def PublicKeys(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~SSHPublicKeysResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='SSHClient', Request='PublicKeys', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PublicKeys)


class Service(Type):
    name = 'Service'
    version = 3
    schema =     {'definitions': {'AddRelation': {'additionalProperties': False,
                                     'properties': {'Endpoints': {'items': {'type': 'string'},
                                                                  'type': 'array'}},
                                     'required': ['Endpoints'],
                                     'type': 'object'},
                     'AddRelationResults': {'additionalProperties': False,
                                            'properties': {'Endpoints': {'patternProperties': {'.*': {'$ref': '#/definitions/Relation'}},
                                                                         'type': 'object'}},
                                            'required': ['Endpoints'],
                                            'type': 'object'},
                     'AddServiceUnits': {'additionalProperties': False,
                                         'properties': {'NumUnits': {'type': 'integer'},
                                                        'Placement': {'items': {'$ref': '#/definitions/Placement'},
                                                                      'type': 'array'},
                                                        'ServiceName': {'type': 'string'}},
                                         'required': ['ServiceName',
                                                      'NumUnits',
                                                      'Placement'],
                                         'type': 'object'},
                     'AddServiceUnitsResults': {'additionalProperties': False,
                                                'properties': {'Units': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                                'required': ['Units'],
                                                'type': 'object'},
                     'Constraints': {'additionalProperties': False,
                                     'properties': {'Count': {'type': 'integer'},
                                                    'Pool': {'type': 'string'},
                                                    'Size': {'type': 'integer'}},
                                     'required': ['Pool', 'Size', 'Count'],
                                     'type': 'object'},
                     'DestroyRelation': {'additionalProperties': False,
                                         'properties': {'Endpoints': {'items': {'type': 'string'},
                                                                      'type': 'array'}},
                                         'required': ['Endpoints'],
                                         'type': 'object'},
                     'DestroyServiceUnits': {'additionalProperties': False,
                                             'properties': {'UnitNames': {'items': {'type': 'string'},
                                                                          'type': 'array'}},
                                             'required': ['UnitNames'],
                                             'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'GetConstraintsResults': {'additionalProperties': False,
                                               'properties': {'Constraints': {'$ref': '#/definitions/Value'}},
                                               'required': ['Constraints'],
                                               'type': 'object'},
                     'GetServiceConstraints': {'additionalProperties': False,
                                               'properties': {'ServiceName': {'type': 'string'}},
                                               'required': ['ServiceName'],
                                               'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Placement': {'additionalProperties': False,
                                   'properties': {'Directive': {'type': 'string'},
                                                  'Scope': {'type': 'string'}},
                                   'required': ['Scope', 'Directive'],
                                   'type': 'object'},
                     'Relation': {'additionalProperties': False,
                                  'properties': {'Interface': {'type': 'string'},
                                                 'Limit': {'type': 'integer'},
                                                 'Name': {'type': 'string'},
                                                 'Optional': {'type': 'boolean'},
                                                 'Role': {'type': 'string'},
                                                 'Scope': {'type': 'string'}},
                                  'required': ['Name',
                                               'Role',
                                               'Interface',
                                               'Optional',
                                               'Limit',
                                               'Scope'],
                                  'type': 'object'},
                     'ServiceCharmRelations': {'additionalProperties': False,
                                               'properties': {'ServiceName': {'type': 'string'}},
                                               'required': ['ServiceName'],
                                               'type': 'object'},
                     'ServiceCharmRelationsResults': {'additionalProperties': False,
                                                      'properties': {'CharmRelations': {'items': {'type': 'string'},
                                                                                        'type': 'array'}},
                                                      'required': ['CharmRelations'],
                                                      'type': 'object'},
                     'ServiceDeploy': {'additionalProperties': False,
                                       'properties': {'Channel': {'type': 'string'},
                                                      'CharmUrl': {'type': 'string'},
                                                      'Config': {'patternProperties': {'.*': {'type': 'string'}},
                                                                 'type': 'object'},
                                                      'ConfigYAML': {'type': 'string'},
                                                      'Constraints': {'$ref': '#/definitions/Value'},
                                                      'EndpointBindings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                           'type': 'object'},
                                                      'NumUnits': {'type': 'integer'},
                                                      'Placement': {'items': {'$ref': '#/definitions/Placement'},
                                                                    'type': 'array'},
                                                      'Resources': {'patternProperties': {'.*': {'type': 'string'}},
                                                                    'type': 'object'},
                                                      'Series': {'type': 'string'},
                                                      'ServiceName': {'type': 'string'},
                                                      'Storage': {'patternProperties': {'.*': {'$ref': '#/definitions/Constraints'}},
                                                                  'type': 'object'}},
                                       'required': ['ServiceName',
                                                    'Series',
                                                    'CharmUrl',
                                                    'Channel',
                                                    'NumUnits',
                                                    'Config',
                                                    'ConfigYAML',
                                                    'Constraints',
                                                    'Placement',
                                                    'Storage',
                                                    'EndpointBindings',
                                                    'Resources'],
                                       'type': 'object'},
                     'ServiceDestroy': {'additionalProperties': False,
                                        'properties': {'ServiceName': {'type': 'string'}},
                                        'required': ['ServiceName'],
                                        'type': 'object'},
                     'ServiceExpose': {'additionalProperties': False,
                                       'properties': {'ServiceName': {'type': 'string'}},
                                       'required': ['ServiceName'],
                                       'type': 'object'},
                     'ServiceGet': {'additionalProperties': False,
                                    'properties': {'ServiceName': {'type': 'string'}},
                                    'required': ['ServiceName'],
                                    'type': 'object'},
                     'ServiceGetResults': {'additionalProperties': False,
                                           'properties': {'Charm': {'type': 'string'},
                                                          'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'},
                                                          'Constraints': {'$ref': '#/definitions/Value'},
                                                          'Service': {'type': 'string'}},
                                           'required': ['Service',
                                                        'Charm',
                                                        'Config',
                                                        'Constraints'],
                                           'type': 'object'},
                     'ServiceMetricCredential': {'additionalProperties': False,
                                                 'properties': {'MetricCredentials': {'items': {'type': 'integer'},
                                                                                      'type': 'array'},
                                                                'ServiceName': {'type': 'string'}},
                                                 'required': ['ServiceName',
                                                              'MetricCredentials'],
                                                 'type': 'object'},
                     'ServiceMetricCredentials': {'additionalProperties': False,
                                                  'properties': {'Creds': {'items': {'$ref': '#/definitions/ServiceMetricCredential'},
                                                                           'type': 'array'}},
                                                  'required': ['Creds'],
                                                  'type': 'object'},
                     'ServiceSet': {'additionalProperties': False,
                                    'properties': {'Options': {'patternProperties': {'.*': {'type': 'string'}},
                                                               'type': 'object'},
                                                   'ServiceName': {'type': 'string'}},
                                    'required': ['ServiceName', 'Options'],
                                    'type': 'object'},
                     'ServiceSetCharm': {'additionalProperties': False,
                                         'properties': {'charmurl': {'type': 'string'},
                                                        'cs-channel': {'type': 'string'},
                                                        'forceseries': {'type': 'boolean'},
                                                        'forceunits': {'type': 'boolean'},
                                                        'resourceids': {'patternProperties': {'.*': {'type': 'string'}},
                                                                        'type': 'object'},
                                                        'servicename': {'type': 'string'}},
                                         'required': ['servicename',
                                                      'charmurl',
                                                      'cs-channel',
                                                      'forceunits',
                                                      'forceseries',
                                                      'resourceids'],
                                         'type': 'object'},
                     'ServiceUnexpose': {'additionalProperties': False,
                                         'properties': {'ServiceName': {'type': 'string'}},
                                         'required': ['ServiceName'],
                                         'type': 'object'},
                     'ServiceUnset': {'additionalProperties': False,
                                      'properties': {'Options': {'items': {'type': 'string'},
                                                                 'type': 'array'},
                                                     'ServiceName': {'type': 'string'}},
                                      'required': ['ServiceName', 'Options'],
                                      'type': 'object'},
                     'ServiceUpdate': {'additionalProperties': False,
                                       'properties': {'CharmUrl': {'type': 'string'},
                                                      'Constraints': {'$ref': '#/definitions/Value'},
                                                      'ForceCharmUrl': {'type': 'boolean'},
                                                      'ForceSeries': {'type': 'boolean'},
                                                      'MinUnits': {'type': 'integer'},
                                                      'ServiceName': {'type': 'string'},
                                                      'SettingsStrings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                          'type': 'object'},
                                                      'SettingsYAML': {'type': 'string'}},
                                       'required': ['ServiceName',
                                                    'CharmUrl',
                                                    'ForceCharmUrl',
                                                    'ForceSeries',
                                                    'MinUnits',
                                                    'SettingsStrings',
                                                    'SettingsYAML',
                                                    'Constraints'],
                                       'type': 'object'},
                     'ServicesDeploy': {'additionalProperties': False,
                                        'properties': {'Services': {'items': {'$ref': '#/definitions/ServiceDeploy'},
                                                                    'type': 'array'}},
                                        'required': ['Services'],
                                        'type': 'object'},
                     'SetConstraints': {'additionalProperties': False,
                                        'properties': {'Constraints': {'$ref': '#/definitions/Value'},
                                                       'ServiceName': {'type': 'string'}},
                                        'required': ['ServiceName', 'Constraints'],
                                        'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'Value': {'additionalProperties': False,
                               'properties': {'arch': {'type': 'string'},
                                              'container': {'type': 'string'},
                                              'cpu-cores': {'type': 'integer'},
                                              'cpu-power': {'type': 'integer'},
                                              'instance-type': {'type': 'string'},
                                              'mem': {'type': 'integer'},
                                              'root-disk': {'type': 'integer'},
                                              'spaces': {'items': {'type': 'string'},
                                                         'type': 'array'},
                                              'tags': {'items': {'type': 'string'},
                                                       'type': 'array'},
                                              'virt-type': {'type': 'string'}},
                               'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddRelation': {'properties': {'Params': {'$ref': '#/definitions/AddRelation'},
                                                   'Result': {'$ref': '#/definitions/AddRelationResults'}},
                                    'type': 'object'},
                    'AddUnits': {'properties': {'Params': {'$ref': '#/definitions/AddServiceUnits'},
                                                'Result': {'$ref': '#/definitions/AddServiceUnitsResults'}},
                                 'type': 'object'},
                    'CharmRelations': {'properties': {'Params': {'$ref': '#/definitions/ServiceCharmRelations'},
                                                      'Result': {'$ref': '#/definitions/ServiceCharmRelationsResults'}},
                                       'type': 'object'},
                    'Deploy': {'properties': {'Params': {'$ref': '#/definitions/ServicesDeploy'},
                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                               'type': 'object'},
                    'Destroy': {'properties': {'Params': {'$ref': '#/definitions/ServiceDestroy'}},
                                'type': 'object'},
                    'DestroyRelation': {'properties': {'Params': {'$ref': '#/definitions/DestroyRelation'}},
                                        'type': 'object'},
                    'DestroyUnits': {'properties': {'Params': {'$ref': '#/definitions/DestroyServiceUnits'}},
                                     'type': 'object'},
                    'Expose': {'properties': {'Params': {'$ref': '#/definitions/ServiceExpose'}},
                               'type': 'object'},
                    'Get': {'properties': {'Params': {'$ref': '#/definitions/ServiceGet'},
                                           'Result': {'$ref': '#/definitions/ServiceGetResults'}},
                            'type': 'object'},
                    'GetCharmURL': {'properties': {'Params': {'$ref': '#/definitions/ServiceGet'},
                                                   'Result': {'$ref': '#/definitions/StringResult'}},
                                    'type': 'object'},
                    'GetConstraints': {'properties': {'Params': {'$ref': '#/definitions/GetServiceConstraints'},
                                                      'Result': {'$ref': '#/definitions/GetConstraintsResults'}},
                                       'type': 'object'},
                    'Set': {'properties': {'Params': {'$ref': '#/definitions/ServiceSet'}},
                            'type': 'object'},
                    'SetCharm': {'properties': {'Params': {'$ref': '#/definitions/ServiceSetCharm'}},
                                 'type': 'object'},
                    'SetConstraints': {'properties': {'Params': {'$ref': '#/definitions/SetConstraints'}},
                                       'type': 'object'},
                    'SetMetricCredentials': {'properties': {'Params': {'$ref': '#/definitions/ServiceMetricCredentials'},
                                                            'Result': {'$ref': '#/definitions/ErrorResults'}},
                                             'type': 'object'},
                    'Unexpose': {'properties': {'Params': {'$ref': '#/definitions/ServiceUnexpose'}},
                                 'type': 'object'},
                    'Unset': {'properties': {'Params': {'$ref': '#/definitions/ServiceUnset'}},
                              'type': 'object'},
                    'Update': {'properties': {'Params': {'$ref': '#/definitions/ServiceUpdate'}},
                               'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AddRelationResults)
    async def AddRelation(self, endpoints):
        '''
        endpoints : typing.Sequence[str]
        Returns -> typing.Mapping[str, ~Relation]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='AddRelation', Version=3, Params=params)
        params['Endpoints'] = endpoints
        reply = await self.rpc(msg)
        return self._map(reply, AddRelation)



    #@ReturnMapping(AddServiceUnitsResults)
    async def AddUnits(self, numunits, placement, servicename):
        '''
        numunits : int
        placement : typing.Sequence[~Placement]
        servicename : str
        Returns -> typing.Sequence[str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='AddUnits', Version=3, Params=params)
        params['NumUnits'] = numunits
        params['Placement'] = placement
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, AddUnits)



    #@ReturnMapping(ServiceCharmRelationsResults)
    async def CharmRelations(self, servicename):
        '''
        servicename : str
        Returns -> typing.Sequence[str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='CharmRelations', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, CharmRelations)



    #@ReturnMapping(ErrorResults)
    async def Deploy(self, services):
        '''
        services : typing.Sequence[~ServiceDeploy]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Deploy', Version=3, Params=params)
        params['Services'] = services
        reply = await self.rpc(msg)
        return self._map(reply, Deploy)



    #@ReturnMapping(None)
    async def Destroy(self, servicename):
        '''
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Destroy', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Destroy)



    #@ReturnMapping(None)
    async def DestroyRelation(self, endpoints):
        '''
        endpoints : typing.Sequence[str]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='DestroyRelation', Version=3, Params=params)
        params['Endpoints'] = endpoints
        reply = await self.rpc(msg)
        return self._map(reply, DestroyRelation)



    #@ReturnMapping(None)
    async def DestroyUnits(self, unitnames):
        '''
        unitnames : typing.Sequence[str]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='DestroyUnits', Version=3, Params=params)
        params['UnitNames'] = unitnames
        reply = await self.rpc(msg)
        return self._map(reply, DestroyUnits)



    #@ReturnMapping(None)
    async def Expose(self, servicename):
        '''
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Expose', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Expose)



    #@ReturnMapping(ServiceGetResults)
    async def Get(self, servicename):
        '''
        servicename : str
        Returns -> typing.Union[str, typing.Mapping[str, typing.Any], ~Value]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Get', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Get)



    #@ReturnMapping(StringResult)
    async def GetCharmURL(self, servicename):
        '''
        servicename : str
        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='GetCharmURL', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, GetCharmURL)



    #@ReturnMapping(GetConstraintsResults)
    async def GetConstraints(self, servicename):
        '''
        servicename : str
        Returns -> ~Value
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='GetConstraints', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, GetConstraints)



    #@ReturnMapping(None)
    async def Set(self, options, servicename):
        '''
        options : typing.Mapping[str, str]
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Set', Version=3, Params=params)
        params['Options'] = options
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Set)



    #@ReturnMapping(None)
    async def SetCharm(self, resourceids, charmurl, forceunits, cs_channel, servicename, forceseries):
        '''
        resourceids : typing.Mapping[str, str]
        charmurl : str
        forceunits : bool
        cs_channel : str
        servicename : str
        forceseries : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='SetCharm', Version=3, Params=params)
        params['resourceids'] = resourceids
        params['charmurl'] = charmurl
        params['forceunits'] = forceunits
        params['cs-channel'] = cs_channel
        params['servicename'] = servicename
        params['forceseries'] = forceseries
        reply = await self.rpc(msg)
        return self._map(reply, SetCharm)



    #@ReturnMapping(None)
    async def SetConstraints(self, constraints, servicename):
        '''
        constraints : ~Value
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='SetConstraints', Version=3, Params=params)
        params['Constraints'] = constraints
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, SetConstraints)



    #@ReturnMapping(ErrorResults)
    async def SetMetricCredentials(self, creds):
        '''
        creds : typing.Sequence[~ServiceMetricCredential]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='SetMetricCredentials', Version=3, Params=params)
        params['Creds'] = creds
        reply = await self.rpc(msg)
        return self._map(reply, SetMetricCredentials)



    #@ReturnMapping(None)
    async def Unexpose(self, servicename):
        '''
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Unexpose', Version=3, Params=params)
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Unexpose)



    #@ReturnMapping(None)
    async def Unset(self, options, servicename):
        '''
        options : typing.Sequence[str]
        servicename : str
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Unset', Version=3, Params=params)
        params['Options'] = options
        params['ServiceName'] = servicename
        reply = await self.rpc(msg)
        return self._map(reply, Unset)



    #@ReturnMapping(None)
    async def Update(self, forceseries, charmurl, settingsstrings, settingsyaml, constraints, servicename, minunits, forcecharmurl):
        '''
        forceseries : bool
        charmurl : str
        settingsstrings : typing.Mapping[str, str]
        settingsyaml : str
        constraints : ~Value
        servicename : str
        minunits : int
        forcecharmurl : bool
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Service', Request='Update', Version=3, Params=params)
        params['ForceSeries'] = forceseries
        params['CharmUrl'] = charmurl
        params['SettingsStrings'] = settingsstrings
        params['SettingsYAML'] = settingsyaml
        params['Constraints'] = constraints
        params['ServiceName'] = servicename
        params['MinUnits'] = minunits
        params['ForceCharmUrl'] = forcecharmurl
        reply = await self.rpc(msg)
        return self._map(reply, Update)


class ServiceScaler(Type):
    name = 'ServiceScaler'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Rescale': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ErrorResults'}},
                                'type': 'object'},
                    'Watch': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def Rescale(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ServiceScaler', Request='Rescale', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Rescale)



    #@ReturnMapping(StringsWatchResult)
    async def Watch(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='ServiceScaler', Request='Watch', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Watch)


class Singular(Type):
    name = 'Singular'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'SingularClaim': {'additionalProperties': False,
                                       'properties': {'ControllerTag': {'type': 'string'},
                                                      'Duration': {'type': 'integer'},
                                                      'ModelTag': {'type': 'string'}},
                                       'required': ['ModelTag',
                                                    'ControllerTag',
                                                    'Duration'],
                                       'type': 'object'},
                     'SingularClaims': {'additionalProperties': False,
                                        'properties': {'Claims': {'items': {'$ref': '#/definitions/SingularClaim'},
                                                                  'type': 'array'}},
                                        'required': ['Claims'],
                                        'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Claim': {'properties': {'Params': {'$ref': '#/definitions/SingularClaims'},
                                             'Result': {'$ref': '#/definitions/ErrorResults'}},
                              'type': 'object'},
                    'Wait': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/ErrorResults'}},
                             'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def Claim(self, claims):
        '''
        claims : typing.Sequence[~SingularClaim]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Singular', Request='Claim', Version=1, Params=params)
        params['Claims'] = claims
        reply = await self.rpc(msg)
        return self._map(reply, Claim)



    #@ReturnMapping(ErrorResults)
    async def Wait(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Singular', Request='Wait', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Wait)


class Spaces(Type):
    name = 'Spaces'
    version = 2
    schema =     {'definitions': {'CreateSpaceParams': {'additionalProperties': False,
                                           'properties': {'ProviderId': {'type': 'string'},
                                                          'Public': {'type': 'boolean'},
                                                          'SpaceTag': {'type': 'string'},
                                                          'SubnetTags': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                           'required': ['SubnetTags',
                                                        'SpaceTag',
                                                        'Public'],
                                           'type': 'object'},
                     'CreateSpacesParams': {'additionalProperties': False,
                                            'properties': {'Spaces': {'items': {'$ref': '#/definitions/CreateSpaceParams'},
                                                                      'type': 'array'}},
                                            'required': ['Spaces'],
                                            'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ListSpacesResults': {'additionalProperties': False,
                                           'properties': {'Results': {'items': {'$ref': '#/definitions/Space'},
                                                                      'type': 'array'}},
                                           'required': ['Results'],
                                           'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'Space': {'additionalProperties': False,
                               'properties': {'Error': {'$ref': '#/definitions/Error'},
                                              'Name': {'type': 'string'},
                                              'Subnets': {'items': {'$ref': '#/definitions/Subnet'},
                                                          'type': 'array'}},
                               'required': ['Name', 'Subnets'],
                               'type': 'object'},
                     'Subnet': {'additionalProperties': False,
                                'properties': {'CIDR': {'type': 'string'},
                                               'Life': {'type': 'string'},
                                               'ProviderId': {'type': 'string'},
                                               'SpaceTag': {'type': 'string'},
                                               'StaticRangeHighIP': {'items': {'type': 'integer'},
                                                                     'type': 'array'},
                                               'StaticRangeLowIP': {'items': {'type': 'integer'},
                                                                    'type': 'array'},
                                               'Status': {'type': 'string'},
                                               'VLANTag': {'type': 'integer'},
                                               'Zones': {'items': {'type': 'string'},
                                                         'type': 'array'}},
                                'required': ['CIDR',
                                             'VLANTag',
                                             'Life',
                                             'SpaceTag',
                                             'Zones'],
                                'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'CreateSpaces': {'properties': {'Params': {'$ref': '#/definitions/CreateSpacesParams'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'ListSpaces': {'properties': {'Result': {'$ref': '#/definitions/ListSpacesResults'}},
                                   'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def CreateSpaces(self, spaces):
        '''
        spaces : typing.Sequence[~CreateSpaceParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Spaces', Request='CreateSpaces', Version=2, Params=params)
        params['Spaces'] = spaces
        reply = await self.rpc(msg)
        return self._map(reply, CreateSpaces)



    #@ReturnMapping(ListSpacesResults)
    async def ListSpaces(self):
        '''

        Returns -> typing.Sequence[~Space]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Spaces', Request='ListSpaces', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ListSpaces)


class StatusHistory(Type):
    name = 'StatusHistory'
    version = 2
    schema =     {'definitions': {'StatusHistoryPruneArgs': {'additionalProperties': False,
                                                'properties': {'MaxLogsPerEntity': {'type': 'integer'}},
                                                'required': ['MaxLogsPerEntity'],
                                                'type': 'object'}},
     'properties': {'Prune': {'properties': {'Params': {'$ref': '#/definitions/StatusHistoryPruneArgs'}},
                              'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(None)
    async def Prune(self, maxlogsperentity):
        '''
        maxlogsperentity : int
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StatusHistory', Request='Prune', Version=2, Params=params)
        params['MaxLogsPerEntity'] = maxlogsperentity
        reply = await self.rpc(msg)
        return self._map(reply, Prune)


class Storage(Type):
    name = 'Storage'
    version = 2
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatus': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Info': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'FilesystemAttachmentInfo': {'additionalProperties': False,
                                                  'properties': {'mountpoint': {'type': 'string'},
                                                                 'read-only': {'type': 'boolean'}},
                                                  'type': 'object'},
                     'FilesystemDetails': {'additionalProperties': False,
                                           'properties': {'filesystemtag': {'type': 'string'},
                                                          'info': {'$ref': '#/definitions/FilesystemInfo'},
                                                          'machineattachments': {'patternProperties': {'.*': {'$ref': '#/definitions/FilesystemAttachmentInfo'}},
                                                                                 'type': 'object'},
                                                          'status': {'$ref': '#/definitions/EntityStatus'},
                                                          'storage': {'$ref': '#/definitions/StorageDetails'},
                                                          'volumetag': {'type': 'string'}},
                                           'required': ['filesystemtag',
                                                        'info',
                                                        'status'],
                                           'type': 'object'},
                     'FilesystemDetailsListResult': {'additionalProperties': False,
                                                     'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                    'result': {'items': {'$ref': '#/definitions/FilesystemDetails'},
                                                                               'type': 'array'}},
                                                     'type': 'object'},
                     'FilesystemDetailsListResults': {'additionalProperties': False,
                                                      'properties': {'results': {'items': {'$ref': '#/definitions/FilesystemDetailsListResult'},
                                                                                 'type': 'array'}},
                                                      'type': 'object'},
                     'FilesystemFilter': {'additionalProperties': False,
                                          'properties': {'machines': {'items': {'type': 'string'},
                                                                      'type': 'array'}},
                                          'type': 'object'},
                     'FilesystemFilters': {'additionalProperties': False,
                                           'properties': {'filters': {'items': {'$ref': '#/definitions/FilesystemFilter'},
                                                                      'type': 'array'}},
                                           'type': 'object'},
                     'FilesystemInfo': {'additionalProperties': False,
                                        'properties': {'filesystemid': {'type': 'string'},
                                                       'size': {'type': 'integer'}},
                                        'required': ['filesystemid', 'size'],
                                        'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'StorageAddParams': {'additionalProperties': False,
                                          'properties': {'StorageName': {'type': 'string'},
                                                         'storage': {'$ref': '#/definitions/StorageConstraints'},
                                                         'unit': {'type': 'string'}},
                                          'required': ['unit',
                                                       'StorageName',
                                                       'storage'],
                                          'type': 'object'},
                     'StorageAttachmentDetails': {'additionalProperties': False,
                                                  'properties': {'location': {'type': 'string'},
                                                                 'machinetag': {'type': 'string'},
                                                                 'storagetag': {'type': 'string'},
                                                                 'unittag': {'type': 'string'}},
                                                  'required': ['storagetag',
                                                               'unittag',
                                                               'machinetag'],
                                                  'type': 'object'},
                     'StorageConstraints': {'additionalProperties': False,
                                            'properties': {'Count': {'type': 'integer'},
                                                           'Pool': {'type': 'string'},
                                                           'Size': {'type': 'integer'}},
                                            'required': ['Pool', 'Size', 'Count'],
                                            'type': 'object'},
                     'StorageDetails': {'additionalProperties': False,
                                        'properties': {'Persistent': {'type': 'boolean'},
                                                       'attachments': {'patternProperties': {'.*': {'$ref': '#/definitions/StorageAttachmentDetails'}},
                                                                       'type': 'object'},
                                                       'kind': {'type': 'integer'},
                                                       'ownertag': {'type': 'string'},
                                                       'status': {'$ref': '#/definitions/EntityStatus'},
                                                       'storagetag': {'type': 'string'}},
                                        'required': ['storagetag',
                                                     'ownertag',
                                                     'kind',
                                                     'status',
                                                     'Persistent'],
                                        'type': 'object'},
                     'StorageDetailsListResult': {'additionalProperties': False,
                                                  'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                 'result': {'items': {'$ref': '#/definitions/StorageDetails'},
                                                                            'type': 'array'}},
                                                  'type': 'object'},
                     'StorageDetailsListResults': {'additionalProperties': False,
                                                   'properties': {'results': {'items': {'$ref': '#/definitions/StorageDetailsListResult'},
                                                                              'type': 'array'}},
                                                   'type': 'object'},
                     'StorageDetailsResult': {'additionalProperties': False,
                                              'properties': {'error': {'$ref': '#/definitions/Error'},
                                                             'result': {'$ref': '#/definitions/StorageDetails'}},
                                              'type': 'object'},
                     'StorageDetailsResults': {'additionalProperties': False,
                                               'properties': {'results': {'items': {'$ref': '#/definitions/StorageDetailsResult'},
                                                                          'type': 'array'}},
                                               'type': 'object'},
                     'StorageFilter': {'additionalProperties': False,
                                       'type': 'object'},
                     'StorageFilters': {'additionalProperties': False,
                                        'properties': {'filters': {'items': {'$ref': '#/definitions/StorageFilter'},
                                                                   'type': 'array'}},
                                        'type': 'object'},
                     'StoragePool': {'additionalProperties': False,
                                     'properties': {'attrs': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                    'name': {'type': 'string'},
                                                    'provider': {'type': 'string'}},
                                     'required': ['name', 'provider', 'attrs'],
                                     'type': 'object'},
                     'StoragePoolFilter': {'additionalProperties': False,
                                           'properties': {'names': {'items': {'type': 'string'},
                                                                    'type': 'array'},
                                                          'providers': {'items': {'type': 'string'},
                                                                        'type': 'array'}},
                                           'type': 'object'},
                     'StoragePoolFilters': {'additionalProperties': False,
                                            'properties': {'filters': {'items': {'$ref': '#/definitions/StoragePoolFilter'},
                                                                       'type': 'array'}},
                                            'type': 'object'},
                     'StoragePoolsResult': {'additionalProperties': False,
                                            'properties': {'error': {'$ref': '#/definitions/Error'},
                                                           'storagepools': {'items': {'$ref': '#/definitions/StoragePool'},
                                                                            'type': 'array'}},
                                            'type': 'object'},
                     'StoragePoolsResults': {'additionalProperties': False,
                                             'properties': {'results': {'items': {'$ref': '#/definitions/StoragePoolsResult'},
                                                                        'type': 'array'}},
                                             'type': 'object'},
                     'StoragesAddParams': {'additionalProperties': False,
                                           'properties': {'storages': {'items': {'$ref': '#/definitions/StorageAddParams'},
                                                                       'type': 'array'}},
                                           'required': ['storages'],
                                           'type': 'object'},
                     'VolumeAttachmentInfo': {'additionalProperties': False,
                                              'properties': {'busaddress': {'type': 'string'},
                                                             'devicelink': {'type': 'string'},
                                                             'devicename': {'type': 'string'},
                                                             'read-only': {'type': 'boolean'}},
                                              'type': 'object'},
                     'VolumeDetails': {'additionalProperties': False,
                                       'properties': {'info': {'$ref': '#/definitions/VolumeInfo'},
                                                      'machineattachments': {'patternProperties': {'.*': {'$ref': '#/definitions/VolumeAttachmentInfo'}},
                                                                             'type': 'object'},
                                                      'status': {'$ref': '#/definitions/EntityStatus'},
                                                      'storage': {'$ref': '#/definitions/StorageDetails'},
                                                      'volumetag': {'type': 'string'}},
                                       'required': ['volumetag', 'info', 'status'],
                                       'type': 'object'},
                     'VolumeDetailsListResult': {'additionalProperties': False,
                                                 'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                'result': {'items': {'$ref': '#/definitions/VolumeDetails'},
                                                                           'type': 'array'}},
                                                 'type': 'object'},
                     'VolumeDetailsListResults': {'additionalProperties': False,
                                                  'properties': {'results': {'items': {'$ref': '#/definitions/VolumeDetailsListResult'},
                                                                             'type': 'array'}},
                                                  'type': 'object'},
                     'VolumeFilter': {'additionalProperties': False,
                                      'properties': {'machines': {'items': {'type': 'string'},
                                                                  'type': 'array'}},
                                      'type': 'object'},
                     'VolumeFilters': {'additionalProperties': False,
                                       'properties': {'filters': {'items': {'$ref': '#/definitions/VolumeFilter'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'VolumeInfo': {'additionalProperties': False,
                                    'properties': {'hardwareid': {'type': 'string'},
                                                   'persistent': {'type': 'boolean'},
                                                   'size': {'type': 'integer'},
                                                   'volumeid': {'type': 'string'}},
                                    'required': ['volumeid', 'size', 'persistent'],
                                    'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddToUnit': {'properties': {'Params': {'$ref': '#/definitions/StoragesAddParams'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'CreatePool': {'properties': {'Params': {'$ref': '#/definitions/StoragePool'}},
                                   'type': 'object'},
                    'ListFilesystems': {'properties': {'Params': {'$ref': '#/definitions/FilesystemFilters'},
                                                       'Result': {'$ref': '#/definitions/FilesystemDetailsListResults'}},
                                        'type': 'object'},
                    'ListPools': {'properties': {'Params': {'$ref': '#/definitions/StoragePoolFilters'},
                                                 'Result': {'$ref': '#/definitions/StoragePoolsResults'}},
                                  'type': 'object'},
                    'ListStorageDetails': {'properties': {'Params': {'$ref': '#/definitions/StorageFilters'},
                                                          'Result': {'$ref': '#/definitions/StorageDetailsListResults'}},
                                           'type': 'object'},
                    'ListVolumes': {'properties': {'Params': {'$ref': '#/definitions/VolumeFilters'},
                                                   'Result': {'$ref': '#/definitions/VolumeDetailsListResults'}},
                                    'type': 'object'},
                    'StorageDetails': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/StorageDetailsResults'}},
                                       'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AddToUnit(self, storages):
        '''
        storages : typing.Sequence[~StorageAddParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='AddToUnit', Version=2, Params=params)
        params['storages'] = storages
        reply = await self.rpc(msg)
        return self._map(reply, AddToUnit)



    #@ReturnMapping(None)
    async def CreatePool(self, name, provider, attrs):
        '''
        name : str
        provider : str
        attrs : typing.Mapping[str, typing.Any]
        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='CreatePool', Version=2, Params=params)
        params['name'] = name
        params['provider'] = provider
        params['attrs'] = attrs
        reply = await self.rpc(msg)
        return self._map(reply, CreatePool)



    #@ReturnMapping(FilesystemDetailsListResults)
    async def ListFilesystems(self, filters):
        '''
        filters : typing.Sequence[~FilesystemFilter]
        Returns -> typing.Sequence[~FilesystemDetailsListResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='ListFilesystems', Version=2, Params=params)
        params['filters'] = filters
        reply = await self.rpc(msg)
        return self._map(reply, ListFilesystems)



    #@ReturnMapping(StoragePoolsResults)
    async def ListPools(self, filters):
        '''
        filters : typing.Sequence[~StoragePoolFilter]
        Returns -> typing.Sequence[~StoragePoolsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='ListPools', Version=2, Params=params)
        params['filters'] = filters
        reply = await self.rpc(msg)
        return self._map(reply, ListPools)



    #@ReturnMapping(StorageDetailsListResults)
    async def ListStorageDetails(self, filters):
        '''
        filters : typing.Sequence[~StorageFilter]
        Returns -> typing.Sequence[~StorageDetailsListResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='ListStorageDetails', Version=2, Params=params)
        params['filters'] = filters
        reply = await self.rpc(msg)
        return self._map(reply, ListStorageDetails)



    #@ReturnMapping(VolumeDetailsListResults)
    async def ListVolumes(self, filters):
        '''
        filters : typing.Sequence[~VolumeFilter]
        Returns -> typing.Sequence[~VolumeDetailsListResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='ListVolumes', Version=2, Params=params)
        params['filters'] = filters
        reply = await self.rpc(msg)
        return self._map(reply, ListVolumes)



    #@ReturnMapping(StorageDetailsResults)
    async def StorageDetails(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StorageDetailsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Storage', Request='StorageDetails', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, StorageDetails)


class StorageProvisioner(Type):
    name = 'StorageProvisioner'
    version = 2
    schema =     {'definitions': {'BlockDevice': {'additionalProperties': False,
                                     'properties': {'BusAddress': {'type': 'string'},
                                                    'DeviceLinks': {'items': {'type': 'string'},
                                                                    'type': 'array'},
                                                    'DeviceName': {'type': 'string'},
                                                    'FilesystemType': {'type': 'string'},
                                                    'HardwareId': {'type': 'string'},
                                                    'InUse': {'type': 'boolean'},
                                                    'Label': {'type': 'string'},
                                                    'MountPoint': {'type': 'string'},
                                                    'Size': {'type': 'integer'},
                                                    'UUID': {'type': 'string'}},
                                     'required': ['DeviceName',
                                                  'DeviceLinks',
                                                  'Label',
                                                  'UUID',
                                                  'HardwareId',
                                                  'BusAddress',
                                                  'Size',
                                                  'FilesystemType',
                                                  'InUse',
                                                  'MountPoint'],
                                     'type': 'object'},
                     'BlockDeviceResult': {'additionalProperties': False,
                                           'properties': {'error': {'$ref': '#/definitions/Error'},
                                                          'result': {'$ref': '#/definitions/BlockDevice'}},
                                           'required': ['result'],
                                           'type': 'object'},
                     'BlockDeviceResults': {'additionalProperties': False,
                                            'properties': {'results': {'items': {'$ref': '#/definitions/BlockDeviceResult'},
                                                                       'type': 'array'}},
                                            'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Filesystem': {'additionalProperties': False,
                                    'properties': {'filesystemtag': {'type': 'string'},
                                                   'info': {'$ref': '#/definitions/FilesystemInfo'},
                                                   'volumetag': {'type': 'string'}},
                                    'required': ['filesystemtag', 'info'],
                                    'type': 'object'},
                     'FilesystemAttachment': {'additionalProperties': False,
                                              'properties': {'filesystemtag': {'type': 'string'},
                                                             'info': {'$ref': '#/definitions/FilesystemAttachmentInfo'},
                                                             'machinetag': {'type': 'string'}},
                                              'required': ['filesystemtag',
                                                           'machinetag',
                                                           'info'],
                                              'type': 'object'},
                     'FilesystemAttachmentInfo': {'additionalProperties': False,
                                                  'properties': {'mountpoint': {'type': 'string'},
                                                                 'read-only': {'type': 'boolean'}},
                                                  'type': 'object'},
                     'FilesystemAttachmentParams': {'additionalProperties': False,
                                                    'properties': {'filesystemid': {'type': 'string'},
                                                                   'filesystemtag': {'type': 'string'},
                                                                   'instanceid': {'type': 'string'},
                                                                   'machinetag': {'type': 'string'},
                                                                   'mountpoint': {'type': 'string'},
                                                                   'provider': {'type': 'string'},
                                                                   'read-only': {'type': 'boolean'}},
                                                    'required': ['filesystemtag',
                                                                 'machinetag',
                                                                 'provider'],
                                                    'type': 'object'},
                     'FilesystemAttachmentParamsResult': {'additionalProperties': False,
                                                          'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                         'result': {'$ref': '#/definitions/FilesystemAttachmentParams'}},
                                                          'required': ['result'],
                                                          'type': 'object'},
                     'FilesystemAttachmentParamsResults': {'additionalProperties': False,
                                                           'properties': {'results': {'items': {'$ref': '#/definitions/FilesystemAttachmentParamsResult'},
                                                                                      'type': 'array'}},
                                                           'type': 'object'},
                     'FilesystemAttachmentResult': {'additionalProperties': False,
                                                    'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                   'result': {'$ref': '#/definitions/FilesystemAttachment'}},
                                                    'required': ['result'],
                                                    'type': 'object'},
                     'FilesystemAttachmentResults': {'additionalProperties': False,
                                                     'properties': {'results': {'items': {'$ref': '#/definitions/FilesystemAttachmentResult'},
                                                                                'type': 'array'}},
                                                     'type': 'object'},
                     'FilesystemAttachments': {'additionalProperties': False,
                                               'properties': {'filesystemattachments': {'items': {'$ref': '#/definitions/FilesystemAttachment'},
                                                                                        'type': 'array'}},
                                               'required': ['filesystemattachments'],
                                               'type': 'object'},
                     'FilesystemInfo': {'additionalProperties': False,
                                        'properties': {'filesystemid': {'type': 'string'},
                                                       'size': {'type': 'integer'}},
                                        'required': ['filesystemid', 'size'],
                                        'type': 'object'},
                     'FilesystemParams': {'additionalProperties': False,
                                          'properties': {'attachment': {'$ref': '#/definitions/FilesystemAttachmentParams'},
                                                         'attributes': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                     'type': 'object'}},
                                                                        'type': 'object'},
                                                         'filesystemtag': {'type': 'string'},
                                                         'provider': {'type': 'string'},
                                                         'size': {'type': 'integer'},
                                                         'tags': {'patternProperties': {'.*': {'type': 'string'}},
                                                                  'type': 'object'},
                                                         'volumetag': {'type': 'string'}},
                                          'required': ['filesystemtag',
                                                       'size',
                                                       'provider'],
                                          'type': 'object'},
                     'FilesystemParamsResult': {'additionalProperties': False,
                                                'properties': {'error': {'$ref': '#/definitions/Error'},
                                                               'result': {'$ref': '#/definitions/FilesystemParams'}},
                                                'required': ['result'],
                                                'type': 'object'},
                     'FilesystemParamsResults': {'additionalProperties': False,
                                                 'properties': {'results': {'items': {'$ref': '#/definitions/FilesystemParamsResult'},
                                                                            'type': 'array'}},
                                                 'type': 'object'},
                     'FilesystemResult': {'additionalProperties': False,
                                          'properties': {'error': {'$ref': '#/definitions/Error'},
                                                         'result': {'$ref': '#/definitions/Filesystem'}},
                                          'required': ['result'],
                                          'type': 'object'},
                     'FilesystemResults': {'additionalProperties': False,
                                           'properties': {'results': {'items': {'$ref': '#/definitions/FilesystemResult'},
                                                                      'type': 'array'}},
                                           'type': 'object'},
                     'Filesystems': {'additionalProperties': False,
                                     'properties': {'filesystems': {'items': {'$ref': '#/definitions/Filesystem'},
                                                                    'type': 'array'}},
                                     'required': ['filesystems'],
                                     'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineStorageId': {'additionalProperties': False,
                                          'properties': {'attachmenttag': {'type': 'string'},
                                                         'machinetag': {'type': 'string'}},
                                          'required': ['machinetag',
                                                       'attachmenttag'],
                                          'type': 'object'},
                     'MachineStorageIds': {'additionalProperties': False,
                                           'properties': {'ids': {'items': {'$ref': '#/definitions/MachineStorageId'},
                                                                  'type': 'array'}},
                                           'required': ['ids'],
                                           'type': 'object'},
                     'MachineStorageIdsWatchResult': {'additionalProperties': False,
                                                      'properties': {'Changes': {'items': {'$ref': '#/definitions/MachineStorageId'},
                                                                                 'type': 'array'},
                                                                     'Error': {'$ref': '#/definitions/Error'},
                                                                     'MachineStorageIdsWatcherId': {'type': 'string'}},
                                                      'required': ['MachineStorageIdsWatcherId',
                                                                   'Changes',
                                                                   'Error'],
                                                      'type': 'object'},
                     'MachineStorageIdsWatchResults': {'additionalProperties': False,
                                                       'properties': {'Results': {'items': {'$ref': '#/definitions/MachineStorageIdsWatchResult'},
                                                                                  'type': 'array'}},
                                                       'required': ['Results'],
                                                       'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'Volume': {'additionalProperties': False,
                                'properties': {'info': {'$ref': '#/definitions/VolumeInfo'},
                                               'volumetag': {'type': 'string'}},
                                'required': ['volumetag', 'info'],
                                'type': 'object'},
                     'VolumeAttachment': {'additionalProperties': False,
                                          'properties': {'info': {'$ref': '#/definitions/VolumeAttachmentInfo'},
                                                         'machinetag': {'type': 'string'},
                                                         'volumetag': {'type': 'string'}},
                                          'required': ['volumetag',
                                                       'machinetag',
                                                       'info'],
                                          'type': 'object'},
                     'VolumeAttachmentInfo': {'additionalProperties': False,
                                              'properties': {'busaddress': {'type': 'string'},
                                                             'devicelink': {'type': 'string'},
                                                             'devicename': {'type': 'string'},
                                                             'read-only': {'type': 'boolean'}},
                                              'type': 'object'},
                     'VolumeAttachmentParams': {'additionalProperties': False,
                                                'properties': {'instanceid': {'type': 'string'},
                                                               'machinetag': {'type': 'string'},
                                                               'provider': {'type': 'string'},
                                                               'read-only': {'type': 'boolean'},
                                                               'volumeid': {'type': 'string'},
                                                               'volumetag': {'type': 'string'}},
                                                'required': ['volumetag',
                                                             'machinetag',
                                                             'provider'],
                                                'type': 'object'},
                     'VolumeAttachmentParamsResult': {'additionalProperties': False,
                                                      'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                     'result': {'$ref': '#/definitions/VolumeAttachmentParams'}},
                                                      'required': ['result'],
                                                      'type': 'object'},
                     'VolumeAttachmentParamsResults': {'additionalProperties': False,
                                                       'properties': {'results': {'items': {'$ref': '#/definitions/VolumeAttachmentParamsResult'},
                                                                                  'type': 'array'}},
                                                       'type': 'object'},
                     'VolumeAttachmentResult': {'additionalProperties': False,
                                                'properties': {'error': {'$ref': '#/definitions/Error'},
                                                               'result': {'$ref': '#/definitions/VolumeAttachment'}},
                                                'required': ['result'],
                                                'type': 'object'},
                     'VolumeAttachmentResults': {'additionalProperties': False,
                                                 'properties': {'results': {'items': {'$ref': '#/definitions/VolumeAttachmentResult'},
                                                                            'type': 'array'}},
                                                 'type': 'object'},
                     'VolumeAttachments': {'additionalProperties': False,
                                           'properties': {'volumeattachments': {'items': {'$ref': '#/definitions/VolumeAttachment'},
                                                                                'type': 'array'}},
                                           'required': ['volumeattachments'],
                                           'type': 'object'},
                     'VolumeInfo': {'additionalProperties': False,
                                    'properties': {'hardwareid': {'type': 'string'},
                                                   'persistent': {'type': 'boolean'},
                                                   'size': {'type': 'integer'},
                                                   'volumeid': {'type': 'string'}},
                                    'required': ['volumeid', 'size', 'persistent'],
                                    'type': 'object'},
                     'VolumeParams': {'additionalProperties': False,
                                      'properties': {'attachment': {'$ref': '#/definitions/VolumeAttachmentParams'},
                                                     'attributes': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                 'type': 'object'}},
                                                                    'type': 'object'},
                                                     'provider': {'type': 'string'},
                                                     'size': {'type': 'integer'},
                                                     'tags': {'patternProperties': {'.*': {'type': 'string'}},
                                                              'type': 'object'},
                                                     'volumetag': {'type': 'string'}},
                                      'required': ['volumetag', 'size', 'provider'],
                                      'type': 'object'},
                     'VolumeParamsResult': {'additionalProperties': False,
                                            'properties': {'error': {'$ref': '#/definitions/Error'},
                                                           'result': {'$ref': '#/definitions/VolumeParams'}},
                                            'required': ['result'],
                                            'type': 'object'},
                     'VolumeParamsResults': {'additionalProperties': False,
                                             'properties': {'results': {'items': {'$ref': '#/definitions/VolumeParamsResult'},
                                                                        'type': 'array'}},
                                             'type': 'object'},
                     'VolumeResult': {'additionalProperties': False,
                                      'properties': {'error': {'$ref': '#/definitions/Error'},
                                                     'result': {'$ref': '#/definitions/Volume'}},
                                      'required': ['result'],
                                      'type': 'object'},
                     'VolumeResults': {'additionalProperties': False,
                                       'properties': {'results': {'items': {'$ref': '#/definitions/VolumeResult'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'Volumes': {'additionalProperties': False,
                                 'properties': {'volumes': {'items': {'$ref': '#/definitions/Volume'},
                                                            'type': 'array'}},
                                 'required': ['volumes'],
                                 'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AttachmentLife': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                      'Result': {'$ref': '#/definitions/LifeResults'}},
                                       'type': 'object'},
                    'EnsureDead': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'FilesystemAttachmentParams': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                                  'Result': {'$ref': '#/definitions/FilesystemAttachmentParamsResults'}},
                                                   'type': 'object'},
                    'FilesystemAttachments': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                             'Result': {'$ref': '#/definitions/FilesystemAttachmentResults'}},
                                              'type': 'object'},
                    'FilesystemParams': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/FilesystemParamsResults'}},
                                         'type': 'object'},
                    'Filesystems': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/FilesystemResults'}},
                                    'type': 'object'},
                    'InstanceId': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StringResults'}},
                                   'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'Remove': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                               'type': 'object'},
                    'RemoveAttachment': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                        'Result': {'$ref': '#/definitions/ErrorResults'}},
                                         'type': 'object'},
                    'SetFilesystemAttachmentInfo': {'properties': {'Params': {'$ref': '#/definitions/FilesystemAttachments'},
                                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                    'type': 'object'},
                    'SetFilesystemInfo': {'properties': {'Params': {'$ref': '#/definitions/Filesystems'},
                                                         'Result': {'$ref': '#/definitions/ErrorResults'}},
                                          'type': 'object'},
                    'SetStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'SetVolumeAttachmentInfo': {'properties': {'Params': {'$ref': '#/definitions/VolumeAttachments'},
                                                               'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                'type': 'object'},
                    'SetVolumeInfo': {'properties': {'Params': {'$ref': '#/definitions/Volumes'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'UpdateStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'VolumeAttachmentParams': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                              'Result': {'$ref': '#/definitions/VolumeAttachmentParamsResults'}},
                                               'type': 'object'},
                    'VolumeAttachments': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                         'Result': {'$ref': '#/definitions/VolumeAttachmentResults'}},
                                          'type': 'object'},
                    'VolumeBlockDevices': {'properties': {'Params': {'$ref': '#/definitions/MachineStorageIds'},
                                                          'Result': {'$ref': '#/definitions/BlockDeviceResults'}},
                                           'type': 'object'},
                    'VolumeParams': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/VolumeParamsResults'}},
                                     'type': 'object'},
                    'Volumes': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/VolumeResults'}},
                                'type': 'object'},
                    'WatchBlockDevices': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                         'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                          'type': 'object'},
                    'WatchFilesystemAttachments': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                  'Result': {'$ref': '#/definitions/MachineStorageIdsWatchResults'}},
                                                   'type': 'object'},
                    'WatchFilesystems': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                         'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'},
                    'WatchMachines': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                      'type': 'object'},
                    'WatchVolumeAttachments': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                              'Result': {'$ref': '#/definitions/MachineStorageIdsWatchResults'}},
                                               'type': 'object'},
                    'WatchVolumes': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                     'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(LifeResults)
    async def AttachmentLife(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='AttachmentLife', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, AttachmentLife)



    #@ReturnMapping(ErrorResults)
    async def EnsureDead(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='EnsureDead', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, EnsureDead)



    #@ReturnMapping(FilesystemAttachmentParamsResults)
    async def FilesystemAttachmentParams(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~FilesystemAttachmentParamsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='FilesystemAttachmentParams', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, FilesystemAttachmentParams)



    #@ReturnMapping(FilesystemAttachmentResults)
    async def FilesystemAttachments(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~FilesystemAttachmentResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='FilesystemAttachments', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, FilesystemAttachments)



    #@ReturnMapping(FilesystemParamsResults)
    async def FilesystemParams(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~FilesystemParamsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='FilesystemParams', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, FilesystemParams)



    #@ReturnMapping(FilesystemResults)
    async def Filesystems(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~FilesystemResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='Filesystems', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Filesystems)



    #@ReturnMapping(StringResults)
    async def InstanceId(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='InstanceId', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, InstanceId)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='Life', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='ModelConfig', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(ErrorResults)
    async def Remove(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='Remove', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Remove)



    #@ReturnMapping(ErrorResults)
    async def RemoveAttachment(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='RemoveAttachment', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, RemoveAttachment)



    #@ReturnMapping(ErrorResults)
    async def SetFilesystemAttachmentInfo(self, filesystemattachments):
        '''
        filesystemattachments : typing.Sequence[~FilesystemAttachment]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='SetFilesystemAttachmentInfo', Version=2, Params=params)
        params['filesystemattachments'] = filesystemattachments
        reply = await self.rpc(msg)
        return self._map(reply, SetFilesystemAttachmentInfo)



    #@ReturnMapping(ErrorResults)
    async def SetFilesystemInfo(self, filesystems):
        '''
        filesystems : typing.Sequence[~Filesystem]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='SetFilesystemInfo', Version=2, Params=params)
        params['filesystems'] = filesystems
        reply = await self.rpc(msg)
        return self._map(reply, SetFilesystemInfo)



    #@ReturnMapping(ErrorResults)
    async def SetStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='SetStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetStatus)



    #@ReturnMapping(ErrorResults)
    async def SetVolumeAttachmentInfo(self, volumeattachments):
        '''
        volumeattachments : typing.Sequence[~VolumeAttachment]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='SetVolumeAttachmentInfo', Version=2, Params=params)
        params['volumeattachments'] = volumeattachments
        reply = await self.rpc(msg)
        return self._map(reply, SetVolumeAttachmentInfo)



    #@ReturnMapping(ErrorResults)
    async def SetVolumeInfo(self, volumes):
        '''
        volumes : typing.Sequence[~Volume]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='SetVolumeInfo', Version=2, Params=params)
        params['volumes'] = volumes
        reply = await self.rpc(msg)
        return self._map(reply, SetVolumeInfo)



    #@ReturnMapping(ErrorResults)
    async def UpdateStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='UpdateStatus', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UpdateStatus)



    #@ReturnMapping(VolumeAttachmentParamsResults)
    async def VolumeAttachmentParams(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~VolumeAttachmentParamsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='VolumeAttachmentParams', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, VolumeAttachmentParams)



    #@ReturnMapping(VolumeAttachmentResults)
    async def VolumeAttachments(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~VolumeAttachmentResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='VolumeAttachments', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, VolumeAttachments)



    #@ReturnMapping(BlockDeviceResults)
    async def VolumeBlockDevices(self, ids):
        '''
        ids : typing.Sequence[~MachineStorageId]
        Returns -> typing.Sequence[~BlockDeviceResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='VolumeBlockDevices', Version=2, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, VolumeBlockDevices)



    #@ReturnMapping(VolumeParamsResults)
    async def VolumeParams(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~VolumeParamsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='VolumeParams', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, VolumeParams)



    #@ReturnMapping(VolumeResults)
    async def Volumes(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~VolumeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='Volumes', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Volumes)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchBlockDevices(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchBlockDevices', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchBlockDevices)



    #@ReturnMapping(MachineStorageIdsWatchResults)
    async def WatchFilesystemAttachments(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachineStorageIdsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchFilesystemAttachments', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchFilesystemAttachments)



    #@ReturnMapping(StringsWatchResults)
    async def WatchFilesystems(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchFilesystems', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchFilesystems)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchForModelConfigChanges', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchMachines(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchMachines', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchMachines)



    #@ReturnMapping(MachineStorageIdsWatchResults)
    async def WatchVolumeAttachments(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachineStorageIdsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchVolumeAttachments', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchVolumeAttachments)



    #@ReturnMapping(StringsWatchResults)
    async def WatchVolumes(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StorageProvisioner', Request='WatchVolumes', Version=2, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchVolumes)


class StringsWatcher(Type):
    name = 'StringsWatcher'
    version = 1
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsWatchResult)
    async def Next(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StringsWatcher', Request='Next', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='StringsWatcher', Request='Stop', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


class Subnets(Type):
    name = 'Subnets'
    version = 2
    schema =     {'definitions': {'AddSubnetParams': {'additionalProperties': False,
                                         'properties': {'SpaceTag': {'type': 'string'},
                                                        'SubnetProviderId': {'type': 'string'},
                                                        'SubnetTag': {'type': 'string'},
                                                        'Zones': {'items': {'type': 'string'},
                                                                  'type': 'array'}},
                                         'required': ['SpaceTag'],
                                         'type': 'object'},
                     'AddSubnetsParams': {'additionalProperties': False,
                                          'properties': {'Subnets': {'items': {'$ref': '#/definitions/AddSubnetParams'},
                                                                     'type': 'array'}},
                                          'required': ['Subnets'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'ListSubnetsResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/Subnet'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'SpaceResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                    'Tag': {'type': 'string'}},
                                     'required': ['Error', 'Tag'],
                                     'type': 'object'},
                     'SpaceResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/SpaceResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Subnet': {'additionalProperties': False,
                                'properties': {'CIDR': {'type': 'string'},
                                               'Life': {'type': 'string'},
                                               'ProviderId': {'type': 'string'},
                                               'SpaceTag': {'type': 'string'},
                                               'StaticRangeHighIP': {'items': {'type': 'integer'},
                                                                     'type': 'array'},
                                               'StaticRangeLowIP': {'items': {'type': 'integer'},
                                                                    'type': 'array'},
                                               'Status': {'type': 'string'},
                                               'VLANTag': {'type': 'integer'},
                                               'Zones': {'items': {'type': 'string'},
                                                         'type': 'array'}},
                                'required': ['CIDR',
                                             'VLANTag',
                                             'Life',
                                             'SpaceTag',
                                             'Zones'],
                                'type': 'object'},
                     'SubnetsFilters': {'additionalProperties': False,
                                        'properties': {'SpaceTag': {'type': 'string'},
                                                       'Zone': {'type': 'string'}},
                                        'type': 'object'},
                     'ZoneResult': {'additionalProperties': False,
                                    'properties': {'Available': {'type': 'boolean'},
                                                   'Error': {'$ref': '#/definitions/Error'},
                                                   'Name': {'type': 'string'}},
                                    'required': ['Error', 'Name', 'Available'],
                                    'type': 'object'},
                     'ZoneResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/ZoneResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddSubnets': {'properties': {'Params': {'$ref': '#/definitions/AddSubnetsParams'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'AllSpaces': {'properties': {'Result': {'$ref': '#/definitions/SpaceResults'}},
                                  'type': 'object'},
                    'AllZones': {'properties': {'Result': {'$ref': '#/definitions/ZoneResults'}},
                                 'type': 'object'},
                    'ListSubnets': {'properties': {'Params': {'$ref': '#/definitions/SubnetsFilters'},
                                                   'Result': {'$ref': '#/definitions/ListSubnetsResults'}},
                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AddSubnets(self, subnets):
        '''
        subnets : typing.Sequence[~AddSubnetParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Subnets', Request='AddSubnets', Version=2, Params=params)
        params['Subnets'] = subnets
        reply = await self.rpc(msg)
        return self._map(reply, AddSubnets)



    #@ReturnMapping(SpaceResults)
    async def AllSpaces(self):
        '''

        Returns -> typing.Sequence[~SpaceResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Subnets', Request='AllSpaces', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, AllSpaces)



    #@ReturnMapping(ZoneResults)
    async def AllZones(self):
        '''

        Returns -> typing.Sequence[~ZoneResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Subnets', Request='AllZones', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, AllZones)



    #@ReturnMapping(ListSubnetsResults)
    async def ListSubnets(self, spacetag, zone):
        '''
        spacetag : str
        zone : str
        Returns -> typing.Sequence[~Subnet]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Subnets', Request='ListSubnets', Version=2, Params=params)
        params['SpaceTag'] = spacetag
        params['Zone'] = zone
        reply = await self.rpc(msg)
        return self._map(reply, ListSubnets)


class Undertaker(Type):
    name = 'Undertaker'
    version = 1
    schema =     {'definitions': {'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'UndertakerModelInfo': {'additionalProperties': False,
                                             'properties': {'GlobalName': {'type': 'string'},
                                                            'IsSystem': {'type': 'boolean'},
                                                            'Life': {'type': 'string'},
                                                            'Name': {'type': 'string'},
                                                            'UUID': {'type': 'string'}},
                                             'required': ['UUID',
                                                          'Name',
                                                          'GlobalName',
                                                          'IsSystem',
                                                          'Life'],
                                             'type': 'object'},
                     'UndertakerModelInfoResult': {'additionalProperties': False,
                                                   'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                  'Result': {'$ref': '#/definitions/UndertakerModelInfo'}},
                                                   'required': ['Error', 'Result'],
                                                   'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'ModelInfo': {'properties': {'Result': {'$ref': '#/definitions/UndertakerModelInfoResult'}},
                                  'type': 'object'},
                    'ProcessDyingModel': {'type': 'object'},
                    'RemoveModel': {'type': 'object'},
                    'SetStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'UpdateStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'WatchModelResources': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                            'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='ModelConfig', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(UndertakerModelInfoResult)
    async def ModelInfo(self):
        '''

        Returns -> typing.Union[~Error, ~UndertakerModelInfo]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='ModelInfo', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelInfo)



    #@ReturnMapping(None)
    async def ProcessDyingModel(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='ProcessDyingModel', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ProcessDyingModel)



    #@ReturnMapping(None)
    async def RemoveModel(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='RemoveModel', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, RemoveModel)



    #@ReturnMapping(ErrorResults)
    async def SetStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='SetStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetStatus)



    #@ReturnMapping(ErrorResults)
    async def UpdateStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='UpdateStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UpdateStatus)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchModelResources(self):
        '''

        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Undertaker', Request='WatchModelResources', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchModelResources)


class UnitAssigner(Type):
    name = 'UnitAssigner'
    version = 1
    schema =     {'definitions': {'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AssignUnits': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'SetAgentStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                      'Result': {'$ref': '#/definitions/ErrorResults'}},
                                       'type': 'object'},
                    'WatchUnitAssignments': {'properties': {'Result': {'$ref': '#/definitions/StringsWatchResult'}},
                                             'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(ErrorResults)
    async def AssignUnits(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UnitAssigner', Request='AssignUnits', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AssignUnits)



    #@ReturnMapping(ErrorResults)
    async def SetAgentStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UnitAssigner', Request='SetAgentStatus', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetAgentStatus)



    #@ReturnMapping(StringsWatchResult)
    async def WatchUnitAssignments(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UnitAssigner', Request='WatchUnitAssignments', Version=1, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchUnitAssignments)


class Uniter(Type):
    name = 'Uniter'
    version = 3
    schema =     {'definitions': {'APIHostPortsResult': {'additionalProperties': False,
                                            'properties': {'Servers': {'items': {'items': {'$ref': '#/definitions/HostPort'},
                                                                                 'type': 'array'},
                                                                       'type': 'array'}},
                                            'required': ['Servers'],
                                            'type': 'object'},
                     'Action': {'additionalProperties': False,
                                'properties': {'name': {'type': 'string'},
                                               'parameters': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                               'receiver': {'type': 'string'},
                                               'tag': {'type': 'string'}},
                                'required': ['tag', 'receiver', 'name'],
                                'type': 'object'},
                     'ActionExecutionResult': {'additionalProperties': False,
                                               'properties': {'actiontag': {'type': 'string'},
                                                              'message': {'type': 'string'},
                                                              'results': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                       'type': 'object'}},
                                                                          'type': 'object'},
                                                              'status': {'type': 'string'}},
                                               'required': ['actiontag', 'status'],
                                               'type': 'object'},
                     'ActionExecutionResults': {'additionalProperties': False,
                                                'properties': {'results': {'items': {'$ref': '#/definitions/ActionExecutionResult'},
                                                                           'type': 'array'}},
                                                'type': 'object'},
                     'ActionResult': {'additionalProperties': False,
                                      'properties': {'action': {'$ref': '#/definitions/Action'},
                                                     'completed': {'format': 'date-time',
                                                                   'type': 'string'},
                                                     'enqueued': {'format': 'date-time',
                                                                  'type': 'string'},
                                                     'error': {'$ref': '#/definitions/Error'},
                                                     'message': {'type': 'string'},
                                                     'output': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                             'type': 'object'}},
                                                                'type': 'object'},
                                                     'started': {'format': 'date-time',
                                                                 'type': 'string'},
                                                     'status': {'type': 'string'}},
                                      'type': 'object'},
                     'ActionResults': {'additionalProperties': False,
                                       'properties': {'results': {'items': {'$ref': '#/definitions/ActionResult'},
                                                                  'type': 'array'}},
                                       'type': 'object'},
                     'Address': {'additionalProperties': False,
                                 'properties': {'Scope': {'type': 'string'},
                                                'SpaceName': {'type': 'string'},
                                                'Type': {'type': 'string'},
                                                'Value': {'type': 'string'}},
                                 'required': ['Value', 'Type', 'Scope'],
                                 'type': 'object'},
                     'BoolResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Result': {'type': 'boolean'}},
                                    'required': ['Error', 'Result'],
                                    'type': 'object'},
                     'BoolResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/BoolResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'BytesResult': {'additionalProperties': False,
                                     'properties': {'Result': {'items': {'type': 'integer'},
                                                               'type': 'array'}},
                                     'required': ['Result'],
                                     'type': 'object'},
                     'CharmURL': {'additionalProperties': False,
                                  'properties': {'URL': {'type': 'string'}},
                                  'required': ['URL'],
                                  'type': 'object'},
                     'CharmURLs': {'additionalProperties': False,
                                   'properties': {'URLs': {'items': {'$ref': '#/definitions/CharmURL'},
                                                           'type': 'array'}},
                                   'required': ['URLs'],
                                   'type': 'object'},
                     'ConfigSettingsResult': {'additionalProperties': False,
                                              'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                             'Settings': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                       'type': 'object'}},
                                                                          'type': 'object'}},
                                              'required': ['Error', 'Settings'],
                                              'type': 'object'},
                     'ConfigSettingsResults': {'additionalProperties': False,
                                               'properties': {'Results': {'items': {'$ref': '#/definitions/ConfigSettingsResult'},
                                                                          'type': 'array'}},
                                               'required': ['Results'],
                                               'type': 'object'},
                     'Endpoint': {'additionalProperties': False,
                                  'properties': {'Relation': {'$ref': '#/definitions/Relation'},
                                                 'ServiceName': {'type': 'string'}},
                                  'required': ['ServiceName', 'Relation'],
                                  'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'EntitiesCharmURL': {'additionalProperties': False,
                                          'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityCharmURL'},
                                                                      'type': 'array'}},
                                          'required': ['Entities'],
                                          'type': 'object'},
                     'EntitiesPortRanges': {'additionalProperties': False,
                                            'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityPortRange'},
                                                                        'type': 'array'}},
                                            'required': ['Entities'],
                                            'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityCharmURL': {'additionalProperties': False,
                                        'properties': {'CharmURL': {'type': 'string'},
                                                       'Tag': {'type': 'string'}},
                                        'required': ['Tag', 'CharmURL'],
                                        'type': 'object'},
                     'EntityPortRange': {'additionalProperties': False,
                                         'properties': {'FromPort': {'type': 'integer'},
                                                        'Protocol': {'type': 'string'},
                                                        'Tag': {'type': 'string'},
                                                        'ToPort': {'type': 'integer'}},
                                         'required': ['Tag',
                                                      'Protocol',
                                                      'FromPort',
                                                      'ToPort'],
                                         'type': 'object'},
                     'EntityStatusArgs': {'additionalProperties': False,
                                          'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                               'type': 'object'}},
                                                                  'type': 'object'},
                                                         'Info': {'type': 'string'},
                                                         'Status': {'type': 'string'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag',
                                                       'Status',
                                                       'Info',
                                                       'Data'],
                                          'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'GetLeadershipSettingsBulkResults': {'additionalProperties': False,
                                                          'properties': {'Results': {'items': {'$ref': '#/definitions/GetLeadershipSettingsResult'},
                                                                                     'type': 'array'}},
                                                          'required': ['Results'],
                                                          'type': 'object'},
                     'GetLeadershipSettingsResult': {'additionalProperties': False,
                                                     'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                    'Settings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                                 'type': 'object'}},
                                                     'required': ['Settings',
                                                                  'Error'],
                                                     'type': 'object'},
                     'HostPort': {'additionalProperties': False,
                                  'properties': {'Address': {'$ref': '#/definitions/Address'},
                                                 'Port': {'type': 'integer'}},
                                  'required': ['Address', 'Port'],
                                  'type': 'object'},
                     'IntResult': {'additionalProperties': False,
                                   'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                  'Result': {'type': 'integer'}},
                                   'required': ['Error', 'Result'],
                                   'type': 'object'},
                     'IntResults': {'additionalProperties': False,
                                    'properties': {'Results': {'items': {'$ref': '#/definitions/IntResult'},
                                                               'type': 'array'}},
                                    'required': ['Results'],
                                    'type': 'object'},
                     'LifeResult': {'additionalProperties': False,
                                    'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                   'Life': {'type': 'string'}},
                                    'required': ['Life', 'Error'],
                                    'type': 'object'},
                     'LifeResults': {'additionalProperties': False,
                                     'properties': {'Results': {'items': {'$ref': '#/definitions/LifeResult'},
                                                                'type': 'array'}},
                                     'required': ['Results'],
                                     'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachinePortRange': {'additionalProperties': False,
                                          'properties': {'PortRange': {'$ref': '#/definitions/PortRange'},
                                                         'RelationTag': {'type': 'string'},
                                                         'UnitTag': {'type': 'string'}},
                                          'required': ['UnitTag',
                                                       'RelationTag',
                                                       'PortRange'],
                                          'type': 'object'},
                     'MachinePortsResult': {'additionalProperties': False,
                                            'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                           'Ports': {'items': {'$ref': '#/definitions/MachinePortRange'},
                                                                     'type': 'array'}},
                                            'required': ['Error', 'Ports'],
                                            'type': 'object'},
                     'MachinePortsResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/MachinePortsResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'MergeLeadershipSettingsBulkParams': {'additionalProperties': False,
                                                           'properties': {'Params': {'items': {'$ref': '#/definitions/MergeLeadershipSettingsParam'},
                                                                                     'type': 'array'}},
                                                           'required': ['Params'],
                                                           'type': 'object'},
                     'MergeLeadershipSettingsParam': {'additionalProperties': False,
                                                      'properties': {'ServiceTag': {'type': 'string'},
                                                                     'Settings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                                  'type': 'object'}},
                                                      'required': ['ServiceTag',
                                                                   'Settings'],
                                                      'type': 'object'},
                     'MeterStatusResult': {'additionalProperties': False,
                                           'properties': {'Code': {'type': 'string'},
                                                          'Error': {'$ref': '#/definitions/Error'},
                                                          'Info': {'type': 'string'}},
                                           'required': ['Code', 'Info', 'Error'],
                                           'type': 'object'},
                     'MeterStatusResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/MeterStatusResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'Metric': {'additionalProperties': False,
                                'properties': {'Key': {'type': 'string'},
                                               'Time': {'format': 'date-time',
                                                        'type': 'string'},
                                               'Value': {'type': 'string'}},
                                'required': ['Key', 'Value', 'Time'],
                                'type': 'object'},
                     'MetricBatch': {'additionalProperties': False,
                                     'properties': {'CharmURL': {'type': 'string'},
                                                    'Created': {'format': 'date-time',
                                                                'type': 'string'},
                                                    'Metrics': {'items': {'$ref': '#/definitions/Metric'},
                                                                'type': 'array'},
                                                    'UUID': {'type': 'string'}},
                                     'required': ['UUID',
                                                  'CharmURL',
                                                  'Created',
                                                  'Metrics'],
                                     'type': 'object'},
                     'MetricBatchParam': {'additionalProperties': False,
                                          'properties': {'Batch': {'$ref': '#/definitions/MetricBatch'},
                                                         'Tag': {'type': 'string'}},
                                          'required': ['Tag', 'Batch'],
                                          'type': 'object'},
                     'MetricBatchParams': {'additionalProperties': False,
                                           'properties': {'Batches': {'items': {'$ref': '#/definitions/MetricBatchParam'},
                                                                      'type': 'array'}},
                                           'required': ['Batches'],
                                           'type': 'object'},
                     'ModelConfigResult': {'additionalProperties': False,
                                           'properties': {'Config': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                                  'type': 'object'}},
                                                                     'type': 'object'}},
                                           'required': ['Config'],
                                           'type': 'object'},
                     'ModelResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                    'Name': {'type': 'string'},
                                                    'UUID': {'type': 'string'}},
                                     'required': ['Error', 'Name', 'UUID'],
                                     'type': 'object'},
                     'NetworkConfig': {'additionalProperties': False,
                                       'properties': {'Address': {'type': 'string'},
                                                      'CIDR': {'type': 'string'},
                                                      'ConfigType': {'type': 'string'},
                                                      'DNSSearchDomains': {'items': {'type': 'string'},
                                                                           'type': 'array'},
                                                      'DNSServers': {'items': {'type': 'string'},
                                                                     'type': 'array'},
                                                      'DeviceIndex': {'type': 'integer'},
                                                      'Disabled': {'type': 'boolean'},
                                                      'GatewayAddress': {'type': 'string'},
                                                      'InterfaceName': {'type': 'string'},
                                                      'InterfaceType': {'type': 'string'},
                                                      'MACAddress': {'type': 'string'},
                                                      'MTU': {'type': 'integer'},
                                                      'NoAutoStart': {'type': 'boolean'},
                                                      'ParentInterfaceName': {'type': 'string'},
                                                      'ProviderAddressId': {'type': 'string'},
                                                      'ProviderId': {'type': 'string'},
                                                      'ProviderSpaceId': {'type': 'string'},
                                                      'ProviderSubnetId': {'type': 'string'},
                                                      'ProviderVLANId': {'type': 'string'},
                                                      'VLANTag': {'type': 'integer'}},
                                       'required': ['DeviceIndex',
                                                    'MACAddress',
                                                    'CIDR',
                                                    'MTU',
                                                    'ProviderId',
                                                    'ProviderSubnetId',
                                                    'ProviderSpaceId',
                                                    'ProviderAddressId',
                                                    'ProviderVLANId',
                                                    'VLANTag',
                                                    'InterfaceName',
                                                    'ParentInterfaceName',
                                                    'InterfaceType',
                                                    'Disabled'],
                                       'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'PortRange': {'additionalProperties': False,
                                   'properties': {'FromPort': {'type': 'integer'},
                                                  'Protocol': {'type': 'string'},
                                                  'ToPort': {'type': 'integer'}},
                                   'required': ['FromPort', 'ToPort', 'Protocol'],
                                   'type': 'object'},
                     'Relation': {'additionalProperties': False,
                                  'properties': {'Interface': {'type': 'string'},
                                                 'Limit': {'type': 'integer'},
                                                 'Name': {'type': 'string'},
                                                 'Optional': {'type': 'boolean'},
                                                 'Role': {'type': 'string'},
                                                 'Scope': {'type': 'string'}},
                                  'required': ['Name',
                                               'Role',
                                               'Interface',
                                               'Optional',
                                               'Limit',
                                               'Scope'],
                                  'type': 'object'},
                     'RelationIds': {'additionalProperties': False,
                                     'properties': {'RelationIds': {'items': {'type': 'integer'},
                                                                    'type': 'array'}},
                                     'required': ['RelationIds'],
                                     'type': 'object'},
                     'RelationResult': {'additionalProperties': False,
                                        'properties': {'Endpoint': {'$ref': '#/definitions/Endpoint'},
                                                       'Error': {'$ref': '#/definitions/Error'},
                                                       'Id': {'type': 'integer'},
                                                       'Key': {'type': 'string'},
                                                       'Life': {'type': 'string'}},
                                        'required': ['Error',
                                                     'Life',
                                                     'Id',
                                                     'Key',
                                                     'Endpoint'],
                                        'type': 'object'},
                     'RelationResults': {'additionalProperties': False,
                                         'properties': {'Results': {'items': {'$ref': '#/definitions/RelationResult'},
                                                                    'type': 'array'}},
                                         'required': ['Results'],
                                         'type': 'object'},
                     'RelationUnit': {'additionalProperties': False,
                                      'properties': {'Relation': {'type': 'string'},
                                                     'Unit': {'type': 'string'}},
                                      'required': ['Relation', 'Unit'],
                                      'type': 'object'},
                     'RelationUnitPair': {'additionalProperties': False,
                                          'properties': {'LocalUnit': {'type': 'string'},
                                                         'Relation': {'type': 'string'},
                                                         'RemoteUnit': {'type': 'string'}},
                                          'required': ['Relation',
                                                       'LocalUnit',
                                                       'RemoteUnit'],
                                          'type': 'object'},
                     'RelationUnitPairs': {'additionalProperties': False,
                                           'properties': {'RelationUnitPairs': {'items': {'$ref': '#/definitions/RelationUnitPair'},
                                                                                'type': 'array'}},
                                           'required': ['RelationUnitPairs'],
                                           'type': 'object'},
                     'RelationUnitSettings': {'additionalProperties': False,
                                              'properties': {'Relation': {'type': 'string'},
                                                             'Settings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                          'type': 'object'},
                                                             'Unit': {'type': 'string'}},
                                              'required': ['Relation',
                                                           'Unit',
                                                           'Settings'],
                                              'type': 'object'},
                     'RelationUnits': {'additionalProperties': False,
                                       'properties': {'RelationUnits': {'items': {'$ref': '#/definitions/RelationUnit'},
                                                                        'type': 'array'}},
                                       'required': ['RelationUnits'],
                                       'type': 'object'},
                     'RelationUnitsChange': {'additionalProperties': False,
                                             'properties': {'Changed': {'patternProperties': {'.*': {'$ref': '#/definitions/UnitSettings'}},
                                                                        'type': 'object'},
                                                            'Departed': {'items': {'type': 'string'},
                                                                         'type': 'array'}},
                                             'required': ['Changed', 'Departed'],
                                             'type': 'object'},
                     'RelationUnitsSettings': {'additionalProperties': False,
                                               'properties': {'RelationUnits': {'items': {'$ref': '#/definitions/RelationUnitSettings'},
                                                                                'type': 'array'}},
                                               'required': ['RelationUnits'],
                                               'type': 'object'},
                     'RelationUnitsWatchResult': {'additionalProperties': False,
                                                  'properties': {'Changes': {'$ref': '#/definitions/RelationUnitsChange'},
                                                                 'Error': {'$ref': '#/definitions/Error'},
                                                                 'RelationUnitsWatcherId': {'type': 'string'}},
                                                  'required': ['RelationUnitsWatcherId',
                                                               'Changes',
                                                               'Error'],
                                                  'type': 'object'},
                     'RelationUnitsWatchResults': {'additionalProperties': False,
                                                   'properties': {'Results': {'items': {'$ref': '#/definitions/RelationUnitsWatchResult'},
                                                                              'type': 'array'}},
                                                   'required': ['Results'],
                                                   'type': 'object'},
                     'ResolvedModeResult': {'additionalProperties': False,
                                            'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                           'Mode': {'type': 'string'}},
                                            'required': ['Error', 'Mode'],
                                            'type': 'object'},
                     'ResolvedModeResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/ResolvedModeResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'ServiceStatusResult': {'additionalProperties': False,
                                             'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                            'Service': {'$ref': '#/definitions/StatusResult'},
                                                            'Units': {'patternProperties': {'.*': {'$ref': '#/definitions/StatusResult'}},
                                                                      'type': 'object'}},
                                             'required': ['Service',
                                                          'Units',
                                                          'Error'],
                                             'type': 'object'},
                     'ServiceStatusResults': {'additionalProperties': False,
                                              'properties': {'Results': {'items': {'$ref': '#/definitions/ServiceStatusResult'},
                                                                         'type': 'array'}},
                                              'required': ['Results'],
                                              'type': 'object'},
                     'SetStatus': {'additionalProperties': False,
                                   'properties': {'Entities': {'items': {'$ref': '#/definitions/EntityStatusArgs'},
                                                               'type': 'array'}},
                                   'required': ['Entities'],
                                   'type': 'object'},
                     'SettingsResult': {'additionalProperties': False,
                                        'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                       'Settings': {'patternProperties': {'.*': {'type': 'string'}},
                                                                    'type': 'object'}},
                                        'required': ['Error', 'Settings'],
                                        'type': 'object'},
                     'SettingsResults': {'additionalProperties': False,
                                         'properties': {'Results': {'items': {'$ref': '#/definitions/SettingsResult'},
                                                                    'type': 'array'}},
                                         'required': ['Results'],
                                         'type': 'object'},
                     'StatusResult': {'additionalProperties': False,
                                      'properties': {'Data': {'patternProperties': {'.*': {'additionalProperties': True,
                                                                                           'type': 'object'}},
                                                              'type': 'object'},
                                                     'Error': {'$ref': '#/definitions/Error'},
                                                     'Id': {'type': 'string'},
                                                     'Info': {'type': 'string'},
                                                     'Life': {'type': 'string'},
                                                     'Since': {'format': 'date-time',
                                                               'type': 'string'},
                                                     'Status': {'type': 'string'}},
                                      'required': ['Error',
                                                   'Id',
                                                   'Life',
                                                   'Status',
                                                   'Info',
                                                   'Data',
                                                   'Since'],
                                      'type': 'object'},
                     'StatusResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StatusResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StorageAddParams': {'additionalProperties': False,
                                          'properties': {'StorageName': {'type': 'string'},
                                                         'storage': {'$ref': '#/definitions/StorageConstraints'},
                                                         'unit': {'type': 'string'}},
                                          'required': ['unit',
                                                       'StorageName',
                                                       'storage'],
                                          'type': 'object'},
                     'StorageAttachment': {'additionalProperties': False,
                                           'properties': {'Kind': {'type': 'integer'},
                                                          'Life': {'type': 'string'},
                                                          'Location': {'type': 'string'},
                                                          'OwnerTag': {'type': 'string'},
                                                          'StorageTag': {'type': 'string'},
                                                          'UnitTag': {'type': 'string'}},
                                           'required': ['StorageTag',
                                                        'OwnerTag',
                                                        'UnitTag',
                                                        'Kind',
                                                        'Location',
                                                        'Life'],
                                           'type': 'object'},
                     'StorageAttachmentId': {'additionalProperties': False,
                                             'properties': {'storagetag': {'type': 'string'},
                                                            'unittag': {'type': 'string'}},
                                             'required': ['storagetag', 'unittag'],
                                             'type': 'object'},
                     'StorageAttachmentIds': {'additionalProperties': False,
                                              'properties': {'ids': {'items': {'$ref': '#/definitions/StorageAttachmentId'},
                                                                     'type': 'array'}},
                                              'required': ['ids'],
                                              'type': 'object'},
                     'StorageAttachmentIdsResult': {'additionalProperties': False,
                                                    'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                   'result': {'$ref': '#/definitions/StorageAttachmentIds'}},
                                                    'required': ['result'],
                                                    'type': 'object'},
                     'StorageAttachmentIdsResults': {'additionalProperties': False,
                                                     'properties': {'results': {'items': {'$ref': '#/definitions/StorageAttachmentIdsResult'},
                                                                                'type': 'array'}},
                                                     'type': 'object'},
                     'StorageAttachmentResult': {'additionalProperties': False,
                                                 'properties': {'error': {'$ref': '#/definitions/Error'},
                                                                'result': {'$ref': '#/definitions/StorageAttachment'}},
                                                 'required': ['result'],
                                                 'type': 'object'},
                     'StorageAttachmentResults': {'additionalProperties': False,
                                                  'properties': {'results': {'items': {'$ref': '#/definitions/StorageAttachmentResult'},
                                                                             'type': 'array'}},
                                                  'type': 'object'},
                     'StorageConstraints': {'additionalProperties': False,
                                            'properties': {'Count': {'type': 'integer'},
                                                           'Pool': {'type': 'string'},
                                                           'Size': {'type': 'integer'}},
                                            'required': ['Pool', 'Size', 'Count'],
                                            'type': 'object'},
                     'StoragesAddParams': {'additionalProperties': False,
                                           'properties': {'storages': {'items': {'$ref': '#/definitions/StorageAddParams'},
                                                                       'type': 'array'}},
                                           'required': ['storages'],
                                           'type': 'object'},
                     'StringBoolResult': {'additionalProperties': False,
                                          'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                         'Ok': {'type': 'boolean'},
                                                         'Result': {'type': 'string'}},
                                          'required': ['Error', 'Result', 'Ok'],
                                          'type': 'object'},
                     'StringBoolResults': {'additionalProperties': False,
                                           'properties': {'Results': {'items': {'$ref': '#/definitions/StringBoolResult'},
                                                                      'type': 'array'}},
                                           'required': ['Results'],
                                           'type': 'object'},
                     'StringResult': {'additionalProperties': False,
                                      'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                     'Result': {'type': 'string'}},
                                      'required': ['Error', 'Result'],
                                      'type': 'object'},
                     'StringResults': {'additionalProperties': False,
                                       'properties': {'Results': {'items': {'$ref': '#/definitions/StringResult'},
                                                                  'type': 'array'}},
                                       'required': ['Results'],
                                       'type': 'object'},
                     'StringsResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Result': {'items': {'type': 'string'},
                                                                 'type': 'array'}},
                                       'required': ['Error', 'Result'],
                                       'type': 'object'},
                     'StringsResults': {'additionalProperties': False,
                                        'properties': {'Results': {'items': {'$ref': '#/definitions/StringsResult'},
                                                                   'type': 'array'}},
                                        'required': ['Results'],
                                        'type': 'object'},
                     'StringsWatchResult': {'additionalProperties': False,
                                            'properties': {'Changes': {'items': {'type': 'string'},
                                                                       'type': 'array'},
                                                           'Error': {'$ref': '#/definitions/Error'},
                                                           'StringsWatcherId': {'type': 'string'}},
                                            'required': ['StringsWatcherId',
                                                         'Changes',
                                                         'Error'],
                                            'type': 'object'},
                     'StringsWatchResults': {'additionalProperties': False,
                                             'properties': {'Results': {'items': {'$ref': '#/definitions/StringsWatchResult'},
                                                                        'type': 'array'}},
                                             'required': ['Results'],
                                             'type': 'object'},
                     'UnitNetworkConfig': {'additionalProperties': False,
                                           'properties': {'BindingName': {'type': 'string'},
                                                          'UnitTag': {'type': 'string'}},
                                           'required': ['UnitTag', 'BindingName'],
                                           'type': 'object'},
                     'UnitNetworkConfigResult': {'additionalProperties': False,
                                                 'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                                'Info': {'items': {'$ref': '#/definitions/NetworkConfig'},
                                                                         'type': 'array'}},
                                                 'required': ['Error', 'Info'],
                                                 'type': 'object'},
                     'UnitNetworkConfigResults': {'additionalProperties': False,
                                                  'properties': {'Results': {'items': {'$ref': '#/definitions/UnitNetworkConfigResult'},
                                                                             'type': 'array'}},
                                                  'required': ['Results'],
                                                  'type': 'object'},
                     'UnitSettings': {'additionalProperties': False,
                                      'properties': {'Version': {'type': 'integer'}},
                                      'required': ['Version'],
                                      'type': 'object'},
                     'UnitsNetworkConfig': {'additionalProperties': False,
                                            'properties': {'Args': {'items': {'$ref': '#/definitions/UnitNetworkConfig'},
                                                                    'type': 'array'}},
                                            'required': ['Args'],
                                            'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'APIAddresses': {'properties': {'Result': {'$ref': '#/definitions/StringsResult'}},
                                     'type': 'object'},
                    'APIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/APIHostPortsResult'}},
                                     'type': 'object'},
                    'Actions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ActionResults'}},
                                'type': 'object'},
                    'AddMetricBatches': {'properties': {'Params': {'$ref': '#/definitions/MetricBatchParams'},
                                                        'Result': {'$ref': '#/definitions/ErrorResults'}},
                                         'type': 'object'},
                    'AddUnitStorage': {'properties': {'Params': {'$ref': '#/definitions/StoragesAddParams'},
                                                      'Result': {'$ref': '#/definitions/ErrorResults'}},
                                       'type': 'object'},
                    'AllMachinePorts': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/MachinePortsResults'}},
                                        'type': 'object'},
                    'AssignedMachine': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/StringResults'}},
                                        'type': 'object'},
                    'AvailabilityZone': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/StringResults'}},
                                         'type': 'object'},
                    'BeginActions': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/ErrorResults'}},
                                     'type': 'object'},
                    'CACert': {'properties': {'Result': {'$ref': '#/definitions/BytesResult'}},
                               'type': 'object'},
                    'CharmArchiveSha256': {'properties': {'Params': {'$ref': '#/definitions/CharmURLs'},
                                                          'Result': {'$ref': '#/definitions/StringResults'}},
                                           'type': 'object'},
                    'CharmModifiedVersion': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                            'Result': {'$ref': '#/definitions/IntResults'}},
                                             'type': 'object'},
                    'CharmURL': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                'Result': {'$ref': '#/definitions/StringBoolResults'}},
                                 'type': 'object'},
                    'ClearResolved': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'ClosePorts': {'properties': {'Params': {'$ref': '#/definitions/EntitiesPortRanges'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'ConfigSettings': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/ConfigSettingsResults'}},
                                       'type': 'object'},
                    'CurrentModel': {'properties': {'Result': {'$ref': '#/definitions/ModelResult'}},
                                     'type': 'object'},
                    'Destroy': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                               'Result': {'$ref': '#/definitions/ErrorResults'}},
                                'type': 'object'},
                    'DestroyAllSubordinates': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                              'Result': {'$ref': '#/definitions/ErrorResults'}},
                                               'type': 'object'},
                    'DestroyUnitStorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                      'type': 'object'},
                    'EnsureDead': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'EnterScope': {'properties': {'Params': {'$ref': '#/definitions/RelationUnits'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'FinishActions': {'properties': {'Params': {'$ref': '#/definitions/ActionExecutionResults'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'GetMeterStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/MeterStatusResults'}},
                                       'type': 'object'},
                    'GetPrincipal': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/StringBoolResults'}},
                                     'type': 'object'},
                    'HasSubordinates': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/BoolResults'}},
                                        'type': 'object'},
                    'JoinedRelations': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/StringsResults'}},
                                        'type': 'object'},
                    'LeaveScope': {'properties': {'Params': {'$ref': '#/definitions/RelationUnits'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'Life': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/LifeResults'}},
                             'type': 'object'},
                    'Merge': {'properties': {'Params': {'$ref': '#/definitions/MergeLeadershipSettingsBulkParams'},
                                             'Result': {'$ref': '#/definitions/ErrorResults'}},
                              'type': 'object'},
                    'ModelConfig': {'properties': {'Result': {'$ref': '#/definitions/ModelConfigResult'}},
                                    'type': 'object'},
                    'ModelUUID': {'properties': {'Result': {'$ref': '#/definitions/StringResult'}},
                                  'type': 'object'},
                    'NetworkConfig': {'properties': {'Params': {'$ref': '#/definitions/UnitsNetworkConfig'},
                                                     'Result': {'$ref': '#/definitions/UnitNetworkConfigResults'}},
                                      'type': 'object'},
                    'OpenPorts': {'properties': {'Params': {'$ref': '#/definitions/EntitiesPortRanges'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'PrivateAddress': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/StringResults'}},
                                       'type': 'object'},
                    'ProviderType': {'properties': {'Result': {'$ref': '#/definitions/StringResult'}},
                                     'type': 'object'},
                    'PublicAddress': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/StringResults'}},
                                      'type': 'object'},
                    'Read': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                            'Result': {'$ref': '#/definitions/GetLeadershipSettingsBulkResults'}},
                             'type': 'object'},
                    'ReadRemoteSettings': {'properties': {'Params': {'$ref': '#/definitions/RelationUnitPairs'},
                                                          'Result': {'$ref': '#/definitions/SettingsResults'}},
                                           'type': 'object'},
                    'ReadSettings': {'properties': {'Params': {'$ref': '#/definitions/RelationUnits'},
                                                    'Result': {'$ref': '#/definitions/SettingsResults'}},
                                     'type': 'object'},
                    'Relation': {'properties': {'Params': {'$ref': '#/definitions/RelationUnits'},
                                                'Result': {'$ref': '#/definitions/RelationResults'}},
                                 'type': 'object'},
                    'RelationById': {'properties': {'Params': {'$ref': '#/definitions/RelationIds'},
                                                    'Result': {'$ref': '#/definitions/RelationResults'}},
                                     'type': 'object'},
                    'RemoveStorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/StorageAttachmentIds'},
                                                                'Result': {'$ref': '#/definitions/ErrorResults'}},
                                                 'type': 'object'},
                    'RequestReboot': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'Resolved': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                'Result': {'$ref': '#/definitions/ResolvedModeResults'}},
                                 'type': 'object'},
                    'ServiceOwner': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                    'Result': {'$ref': '#/definitions/StringResults'}},
                                     'type': 'object'},
                    'ServiceStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                     'Result': {'$ref': '#/definitions/ServiceStatusResults'}},
                                      'type': 'object'},
                    'SetAgentStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                      'Result': {'$ref': '#/definitions/ErrorResults'}},
                                       'type': 'object'},
                    'SetCharmURL': {'properties': {'Params': {'$ref': '#/definitions/EntitiesCharmURL'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'SetServiceStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                        'Result': {'$ref': '#/definitions/ErrorResults'}},
                                         'type': 'object'},
                    'SetStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                 'Result': {'$ref': '#/definitions/ErrorResults'}},
                                  'type': 'object'},
                    'SetUnitStatus': {'properties': {'Params': {'$ref': '#/definitions/SetStatus'},
                                                     'Result': {'$ref': '#/definitions/ErrorResults'}},
                                      'type': 'object'},
                    'StorageAttachmentLife': {'properties': {'Params': {'$ref': '#/definitions/StorageAttachmentIds'},
                                                             'Result': {'$ref': '#/definitions/LifeResults'}},
                                              'type': 'object'},
                    'StorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/StorageAttachmentIds'},
                                                          'Result': {'$ref': '#/definitions/StorageAttachmentResults'}},
                                           'type': 'object'},
                    'UnitStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/StatusResults'}},
                                   'type': 'object'},
                    'UnitStorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                              'Result': {'$ref': '#/definitions/StorageAttachmentIdsResults'}},
                                               'type': 'object'},
                    'UpdateSettings': {'properties': {'Params': {'$ref': '#/definitions/RelationUnitsSettings'},
                                                      'Result': {'$ref': '#/definitions/ErrorResults'}},
                                       'type': 'object'},
                    'Watch': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                              'type': 'object'},
                    'WatchAPIHostPorts': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                          'type': 'object'},
                    'WatchActionNotifications': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                                 'type': 'object'},
                    'WatchConfigSettings': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                           'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                            'type': 'object'},
                    'WatchForModelConfigChanges': {'properties': {'Result': {'$ref': '#/definitions/NotifyWatchResult'}},
                                                   'type': 'object'},
                    'WatchLeadershipSettings': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                               'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                                'type': 'object'},
                    'WatchMeterStatus': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                        'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                         'type': 'object'},
                    'WatchRelationUnits': {'properties': {'Params': {'$ref': '#/definitions/RelationUnits'},
                                                          'Result': {'$ref': '#/definitions/RelationUnitsWatchResults'}},
                                           'type': 'object'},
                    'WatchServiceRelations': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                             'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                              'type': 'object'},
                    'WatchStorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/StorageAttachmentIds'},
                                                               'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                                'type': 'object'},
                    'WatchUnitAddresses': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                          'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                           'type': 'object'},
                    'WatchUnitStorageAttachments': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                   'Result': {'$ref': '#/definitions/StringsWatchResults'}},
                                                    'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(StringsResult)
    async def APIAddresses(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[str]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='APIAddresses', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIAddresses)



    #@ReturnMapping(APIHostPortsResult)
    async def APIHostPorts(self):
        '''

        Returns -> typing.Sequence[~HostPort]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='APIHostPorts', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, APIHostPorts)



    #@ReturnMapping(ActionResults)
    async def Actions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ActionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Actions', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Actions)



    #@ReturnMapping(ErrorResults)
    async def AddMetricBatches(self, batches):
        '''
        batches : typing.Sequence[~MetricBatchParam]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='AddMetricBatches', Version=3, Params=params)
        params['Batches'] = batches
        reply = await self.rpc(msg)
        return self._map(reply, AddMetricBatches)



    #@ReturnMapping(ErrorResults)
    async def AddUnitStorage(self, storages):
        '''
        storages : typing.Sequence[~StorageAddParams]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='AddUnitStorage', Version=3, Params=params)
        params['storages'] = storages
        reply = await self.rpc(msg)
        return self._map(reply, AddUnitStorage)



    #@ReturnMapping(MachinePortsResults)
    async def AllMachinePorts(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MachinePortsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='AllMachinePorts', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AllMachinePorts)



    #@ReturnMapping(StringResults)
    async def AssignedMachine(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='AssignedMachine', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AssignedMachine)



    #@ReturnMapping(StringResults)
    async def AvailabilityZone(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='AvailabilityZone', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, AvailabilityZone)



    #@ReturnMapping(ErrorResults)
    async def BeginActions(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='BeginActions', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, BeginActions)



    #@ReturnMapping(BytesResult)
    async def CACert(self):
        '''

        Returns -> typing.Sequence[int]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='CACert', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CACert)



    #@ReturnMapping(StringResults)
    async def CharmArchiveSha256(self, urls):
        '''
        urls : typing.Sequence[~CharmURL]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='CharmArchiveSha256', Version=3, Params=params)
        params['URLs'] = urls
        reply = await self.rpc(msg)
        return self._map(reply, CharmArchiveSha256)



    #@ReturnMapping(IntResults)
    async def CharmModifiedVersion(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~IntResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='CharmModifiedVersion', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, CharmModifiedVersion)



    #@ReturnMapping(StringBoolResults)
    async def CharmURL(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringBoolResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='CharmURL', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, CharmURL)



    #@ReturnMapping(ErrorResults)
    async def ClearResolved(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ClearResolved', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ClearResolved)



    #@ReturnMapping(ErrorResults)
    async def ClosePorts(self, entities):
        '''
        entities : typing.Sequence[~EntityPortRange]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ClosePorts', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ClosePorts)



    #@ReturnMapping(ConfigSettingsResults)
    async def ConfigSettings(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ConfigSettingsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ConfigSettings', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ConfigSettings)



    #@ReturnMapping(ModelResult)
    async def CurrentModel(self):
        '''

        Returns -> typing.Union[str, ~Error]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='CurrentModel', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, CurrentModel)



    #@ReturnMapping(ErrorResults)
    async def Destroy(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Destroy', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Destroy)



    #@ReturnMapping(ErrorResults)
    async def DestroyAllSubordinates(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='DestroyAllSubordinates', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, DestroyAllSubordinates)



    #@ReturnMapping(ErrorResults)
    async def DestroyUnitStorageAttachments(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='DestroyUnitStorageAttachments', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, DestroyUnitStorageAttachments)



    #@ReturnMapping(ErrorResults)
    async def EnsureDead(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='EnsureDead', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, EnsureDead)



    #@ReturnMapping(ErrorResults)
    async def EnterScope(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnit]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='EnterScope', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, EnterScope)



    #@ReturnMapping(ErrorResults)
    async def FinishActions(self, results):
        '''
        results : typing.Sequence[~ActionExecutionResult]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='FinishActions', Version=3, Params=params)
        params['results'] = results
        reply = await self.rpc(msg)
        return self._map(reply, FinishActions)



    #@ReturnMapping(MeterStatusResults)
    async def GetMeterStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MeterStatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='GetMeterStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetMeterStatus)



    #@ReturnMapping(StringBoolResults)
    async def GetPrincipal(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringBoolResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='GetPrincipal', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, GetPrincipal)



    #@ReturnMapping(BoolResults)
    async def HasSubordinates(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~BoolResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='HasSubordinates', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, HasSubordinates)



    #@ReturnMapping(StringsResults)
    async def JoinedRelations(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='JoinedRelations', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, JoinedRelations)



    #@ReturnMapping(ErrorResults)
    async def LeaveScope(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnit]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='LeaveScope', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, LeaveScope)



    #@ReturnMapping(LifeResults)
    async def Life(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Life', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Life)



    #@ReturnMapping(ErrorResults)
    async def Merge(self, params):
        '''
        params : typing.Sequence[~MergeLeadershipSettingsParam]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Merge', Version=3, Params=params)
        params['Params'] = params
        reply = await self.rpc(msg)
        return self._map(reply, Merge)



    #@ReturnMapping(ModelConfigResult)
    async def ModelConfig(self):
        '''

        Returns -> typing.Mapping[str, typing.Any]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ModelConfig', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelConfig)



    #@ReturnMapping(StringResult)
    async def ModelUUID(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ModelUUID', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ModelUUID)



    #@ReturnMapping(UnitNetworkConfigResults)
    async def NetworkConfig(self, args):
        '''
        args : typing.Sequence[~UnitNetworkConfig]
        Returns -> typing.Sequence[~UnitNetworkConfigResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='NetworkConfig', Version=3, Params=params)
        params['Args'] = args
        reply = await self.rpc(msg)
        return self._map(reply, NetworkConfig)



    #@ReturnMapping(ErrorResults)
    async def OpenPorts(self, entities):
        '''
        entities : typing.Sequence[~EntityPortRange]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='OpenPorts', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, OpenPorts)



    #@ReturnMapping(StringResults)
    async def PrivateAddress(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='PrivateAddress', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PrivateAddress)



    #@ReturnMapping(StringResult)
    async def ProviderType(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ProviderType', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, ProviderType)



    #@ReturnMapping(StringResults)
    async def PublicAddress(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='PublicAddress', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, PublicAddress)



    #@ReturnMapping(GetLeadershipSettingsBulkResults)
    async def Read(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~GetLeadershipSettingsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Read', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Read)



    #@ReturnMapping(SettingsResults)
    async def ReadRemoteSettings(self, relationunitpairs):
        '''
        relationunitpairs : typing.Sequence[~RelationUnitPair]
        Returns -> typing.Sequence[~SettingsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ReadRemoteSettings', Version=3, Params=params)
        params['RelationUnitPairs'] = relationunitpairs
        reply = await self.rpc(msg)
        return self._map(reply, ReadRemoteSettings)



    #@ReturnMapping(SettingsResults)
    async def ReadSettings(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnit]
        Returns -> typing.Sequence[~SettingsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ReadSettings', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, ReadSettings)



    #@ReturnMapping(RelationResults)
    async def Relation(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnit]
        Returns -> typing.Sequence[~RelationResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Relation', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, Relation)



    #@ReturnMapping(RelationResults)
    async def RelationById(self, relationids):
        '''
        relationids : typing.Sequence[int]
        Returns -> typing.Sequence[~RelationResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='RelationById', Version=3, Params=params)
        params['RelationIds'] = relationids
        reply = await self.rpc(msg)
        return self._map(reply, RelationById)



    #@ReturnMapping(ErrorResults)
    async def RemoveStorageAttachments(self, ids):
        '''
        ids : typing.Sequence[~StorageAttachmentId]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='RemoveStorageAttachments', Version=3, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, RemoveStorageAttachments)



    #@ReturnMapping(ErrorResults)
    async def RequestReboot(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='RequestReboot', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, RequestReboot)



    #@ReturnMapping(ResolvedModeResults)
    async def Resolved(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ResolvedModeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Resolved', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Resolved)



    #@ReturnMapping(StringResults)
    async def ServiceOwner(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ServiceOwner', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ServiceOwner)



    #@ReturnMapping(ServiceStatusResults)
    async def ServiceStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ServiceStatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='ServiceStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, ServiceStatus)



    #@ReturnMapping(ErrorResults)
    async def SetAgentStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='SetAgentStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetAgentStatus)



    #@ReturnMapping(ErrorResults)
    async def SetCharmURL(self, entities):
        '''
        entities : typing.Sequence[~EntityCharmURL]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='SetCharmURL', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetCharmURL)



    #@ReturnMapping(ErrorResults)
    async def SetServiceStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='SetServiceStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetServiceStatus)



    #@ReturnMapping(ErrorResults)
    async def SetStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='SetStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetStatus)



    #@ReturnMapping(ErrorResults)
    async def SetUnitStatus(self, entities):
        '''
        entities : typing.Sequence[~EntityStatusArgs]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='SetUnitStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, SetUnitStatus)



    #@ReturnMapping(LifeResults)
    async def StorageAttachmentLife(self, ids):
        '''
        ids : typing.Sequence[~StorageAttachmentId]
        Returns -> typing.Sequence[~LifeResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='StorageAttachmentLife', Version=3, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, StorageAttachmentLife)



    #@ReturnMapping(StorageAttachmentResults)
    async def StorageAttachments(self, ids):
        '''
        ids : typing.Sequence[~StorageAttachmentId]
        Returns -> typing.Sequence[~StorageAttachmentResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='StorageAttachments', Version=3, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, StorageAttachments)



    #@ReturnMapping(StatusResults)
    async def UnitStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StatusResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='UnitStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UnitStatus)



    #@ReturnMapping(StorageAttachmentIdsResults)
    async def UnitStorageAttachments(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StorageAttachmentIdsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='UnitStorageAttachments', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, UnitStorageAttachments)



    #@ReturnMapping(ErrorResults)
    async def UpdateSettings(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnitSettings]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='UpdateSettings', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, UpdateSettings)



    #@ReturnMapping(NotifyWatchResults)
    async def Watch(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='Watch', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Watch)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchAPIHostPorts(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchAPIHostPorts', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchAPIHostPorts)



    #@ReturnMapping(StringsWatchResults)
    async def WatchActionNotifications(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchActionNotifications', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchActionNotifications)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchConfigSettings(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchConfigSettings', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchConfigSettings)



    #@ReturnMapping(NotifyWatchResult)
    async def WatchForModelConfigChanges(self):
        '''

        Returns -> typing.Union[~Error, str]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchForModelConfigChanges', Version=3, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, WatchForModelConfigChanges)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchLeadershipSettings(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchLeadershipSettings', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchLeadershipSettings)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchMeterStatus(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchMeterStatus', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchMeterStatus)



    #@ReturnMapping(RelationUnitsWatchResults)
    async def WatchRelationUnits(self, relationunits):
        '''
        relationunits : typing.Sequence[~RelationUnit]
        Returns -> typing.Sequence[~RelationUnitsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchRelationUnits', Version=3, Params=params)
        params['RelationUnits'] = relationunits
        reply = await self.rpc(msg)
        return self._map(reply, WatchRelationUnits)



    #@ReturnMapping(StringsWatchResults)
    async def WatchServiceRelations(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchServiceRelations', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchServiceRelations)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchStorageAttachments(self, ids):
        '''
        ids : typing.Sequence[~StorageAttachmentId]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchStorageAttachments', Version=3, Params=params)
        params['ids'] = ids
        reply = await self.rpc(msg)
        return self._map(reply, WatchStorageAttachments)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchUnitAddresses(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchUnitAddresses', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchUnitAddresses)



    #@ReturnMapping(StringsWatchResults)
    async def WatchUnitStorageAttachments(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~StringsWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Uniter', Request='WatchUnitStorageAttachments', Version=3, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchUnitStorageAttachments)


class Upgrader(Type):
    name = 'Upgrader'
    version = 1
    schema =     {'definitions': {'Binary': {'additionalProperties': False,
                                'properties': {'Arch': {'type': 'string'},
                                               'Number': {'$ref': '#/definitions/Number'},
                                               'Series': {'type': 'string'}},
                                'required': ['Number', 'Series', 'Arch'],
                                'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'EntitiesVersion': {'additionalProperties': False,
                                         'properties': {'AgentTools': {'items': {'$ref': '#/definitions/EntityVersion'},
                                                                       'type': 'array'}},
                                         'required': ['AgentTools'],
                                         'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityVersion': {'additionalProperties': False,
                                       'properties': {'Tag': {'type': 'string'},
                                                      'Tools': {'$ref': '#/definitions/Version'}},
                                       'required': ['Tag', 'Tools'],
                                       'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'NotifyWatchResult': {'additionalProperties': False,
                                           'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                          'NotifyWatcherId': {'type': 'string'}},
                                           'required': ['NotifyWatcherId', 'Error'],
                                           'type': 'object'},
                     'NotifyWatchResults': {'additionalProperties': False,
                                            'properties': {'Results': {'items': {'$ref': '#/definitions/NotifyWatchResult'},
                                                                       'type': 'array'}},
                                            'required': ['Results'],
                                            'type': 'object'},
                     'Number': {'additionalProperties': False,
                                'properties': {'Build': {'type': 'integer'},
                                               'Major': {'type': 'integer'},
                                               'Minor': {'type': 'integer'},
                                               'Patch': {'type': 'integer'},
                                               'Tag': {'type': 'string'}},
                                'required': ['Major',
                                             'Minor',
                                             'Tag',
                                             'Patch',
                                             'Build'],
                                'type': 'object'},
                     'Tools': {'additionalProperties': False,
                               'properties': {'sha256': {'type': 'string'},
                                              'size': {'type': 'integer'},
                                              'url': {'type': 'string'},
                                              'version': {'$ref': '#/definitions/Binary'}},
                               'required': ['version', 'url', 'size'],
                               'type': 'object'},
                     'ToolsResult': {'additionalProperties': False,
                                     'properties': {'DisableSSLHostnameVerification': {'type': 'boolean'},
                                                    'Error': {'$ref': '#/definitions/Error'},
                                                    'ToolsList': {'items': {'$ref': '#/definitions/Tools'},
                                                                  'type': 'array'}},
                                     'required': ['ToolsList',
                                                  'DisableSSLHostnameVerification',
                                                  'Error'],
                                     'type': 'object'},
                     'ToolsResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ToolsResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Version': {'additionalProperties': False,
                                 'properties': {'Version': {'$ref': '#/definitions/Binary'}},
                                 'required': ['Version'],
                                 'type': 'object'},
                     'VersionResult': {'additionalProperties': False,
                                       'properties': {'Error': {'$ref': '#/definitions/Error'},
                                                      'Version': {'$ref': '#/definitions/Number'}},
                                       'required': ['Version', 'Error'],
                                       'type': 'object'},
                     'VersionResults': {'additionalProperties': False,
                                        'properties': {'Results': {'items': {'$ref': '#/definitions/VersionResult'},
                                                                   'type': 'array'}},
                                        'required': ['Results'],
                                        'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'DesiredVersion': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                      'Result': {'$ref': '#/definitions/VersionResults'}},
                                       'type': 'object'},
                    'SetTools': {'properties': {'Params': {'$ref': '#/definitions/EntitiesVersion'},
                                                'Result': {'$ref': '#/definitions/ErrorResults'}},
                                 'type': 'object'},
                    'Tools': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                             'Result': {'$ref': '#/definitions/ToolsResults'}},
                              'type': 'object'},
                    'WatchAPIVersion': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                       'Result': {'$ref': '#/definitions/NotifyWatchResults'}},
                                        'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(VersionResults)
    async def DesiredVersion(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~VersionResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Upgrader', Request='DesiredVersion', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, DesiredVersion)



    #@ReturnMapping(ErrorResults)
    async def SetTools(self, agenttools):
        '''
        agenttools : typing.Sequence[~EntityVersion]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Upgrader', Request='SetTools', Version=1, Params=params)
        params['AgentTools'] = agenttools
        reply = await self.rpc(msg)
        return self._map(reply, SetTools)



    #@ReturnMapping(ToolsResults)
    async def Tools(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ToolsResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Upgrader', Request='Tools', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, Tools)



    #@ReturnMapping(NotifyWatchResults)
    async def WatchAPIVersion(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~NotifyWatchResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='Upgrader', Request='WatchAPIVersion', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, WatchAPIVersion)


class UserManager(Type):
    name = 'UserManager'
    version = 1
    schema =     {'definitions': {'AddUser': {'additionalProperties': False,
                                 'properties': {'display-name': {'type': 'string'},
                                                'model-access-permission': {'type': 'string'},
                                                'password': {'type': 'string'},
                                                'shared-model-tags': {'items': {'type': 'string'},
                                                                      'type': 'array'},
                                                'username': {'type': 'string'}},
                                 'required': ['username',
                                              'display-name',
                                              'shared-model-tags'],
                                 'type': 'object'},
                     'AddUserResult': {'additionalProperties': False,
                                       'properties': {'error': {'$ref': '#/definitions/Error'},
                                                      'secret-key': {'items': {'type': 'integer'},
                                                                     'type': 'array'},
                                                      'tag': {'type': 'string'}},
                                       'type': 'object'},
                     'AddUserResults': {'additionalProperties': False,
                                        'properties': {'results': {'items': {'$ref': '#/definitions/AddUserResult'},
                                                                   'type': 'array'}},
                                        'required': ['results'],
                                        'type': 'object'},
                     'AddUsers': {'additionalProperties': False,
                                  'properties': {'users': {'items': {'$ref': '#/definitions/AddUser'},
                                                           'type': 'array'}},
                                  'required': ['users'],
                                  'type': 'object'},
                     'Entities': {'additionalProperties': False,
                                  'properties': {'Entities': {'items': {'$ref': '#/definitions/Entity'},
                                                              'type': 'array'}},
                                  'required': ['Entities'],
                                  'type': 'object'},
                     'Entity': {'additionalProperties': False,
                                'properties': {'Tag': {'type': 'string'}},
                                'required': ['Tag'],
                                'type': 'object'},
                     'EntityPassword': {'additionalProperties': False,
                                        'properties': {'Password': {'type': 'string'},
                                                       'Tag': {'type': 'string'}},
                                        'required': ['Tag', 'Password'],
                                        'type': 'object'},
                     'EntityPasswords': {'additionalProperties': False,
                                         'properties': {'Changes': {'items': {'$ref': '#/definitions/EntityPassword'},
                                                                    'type': 'array'}},
                                         'required': ['Changes'],
                                         'type': 'object'},
                     'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'ErrorResult': {'additionalProperties': False,
                                     'properties': {'Error': {'$ref': '#/definitions/Error'}},
                                     'required': ['Error'],
                                     'type': 'object'},
                     'ErrorResults': {'additionalProperties': False,
                                      'properties': {'Results': {'items': {'$ref': '#/definitions/ErrorResult'},
                                                                 'type': 'array'}},
                                      'required': ['Results'],
                                      'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MacaroonResult': {'additionalProperties': False,
                                        'properties': {'error': {'$ref': '#/definitions/Error'},
                                                       'result': {'$ref': '#/definitions/Macaroon'}},
                                        'type': 'object'},
                     'MacaroonResults': {'additionalProperties': False,
                                         'properties': {'results': {'items': {'$ref': '#/definitions/MacaroonResult'},
                                                                    'type': 'array'}},
                                         'required': ['results'],
                                         'type': 'object'},
                     'UserInfo': {'additionalProperties': False,
                                  'properties': {'created-by': {'type': 'string'},
                                                 'date-created': {'format': 'date-time',
                                                                  'type': 'string'},
                                                 'disabled': {'type': 'boolean'},
                                                 'display-name': {'type': 'string'},
                                                 'last-connection': {'format': 'date-time',
                                                                     'type': 'string'},
                                                 'username': {'type': 'string'}},
                                  'required': ['username',
                                               'display-name',
                                               'created-by',
                                               'date-created',
                                               'disabled'],
                                  'type': 'object'},
                     'UserInfoRequest': {'additionalProperties': False,
                                         'properties': {'entities': {'items': {'$ref': '#/definitions/Entity'},
                                                                     'type': 'array'},
                                                        'include-disabled': {'type': 'boolean'}},
                                         'required': ['entities',
                                                      'include-disabled'],
                                         'type': 'object'},
                     'UserInfoResult': {'additionalProperties': False,
                                        'properties': {'error': {'$ref': '#/definitions/Error'},
                                                       'result': {'$ref': '#/definitions/UserInfo'}},
                                        'type': 'object'},
                     'UserInfoResults': {'additionalProperties': False,
                                         'properties': {'results': {'items': {'$ref': '#/definitions/UserInfoResult'},
                                                                    'type': 'array'}},
                                         'required': ['results'],
                                         'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'AddUser': {'properties': {'Params': {'$ref': '#/definitions/AddUsers'},
                                               'Result': {'$ref': '#/definitions/AddUserResults'}},
                                'type': 'object'},
                    'CreateLocalLoginMacaroon': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                                'Result': {'$ref': '#/definitions/MacaroonResults'}},
                                                 'type': 'object'},
                    'DisableUser': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'EnableUser': {'properties': {'Params': {'$ref': '#/definitions/Entities'},
                                                  'Result': {'$ref': '#/definitions/ErrorResults'}},
                                   'type': 'object'},
                    'SetPassword': {'properties': {'Params': {'$ref': '#/definitions/EntityPasswords'},
                                                   'Result': {'$ref': '#/definitions/ErrorResults'}},
                                    'type': 'object'},
                    'UserInfo': {'properties': {'Params': {'$ref': '#/definitions/UserInfoRequest'},
                                                'Result': {'$ref': '#/definitions/UserInfoResults'}},
                                 'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(AddUserResults)
    async def AddUser(self, users):
        '''
        users : typing.Sequence[~AddUser]
        Returns -> typing.Sequence[~AddUserResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='AddUser', Version=1, Params=params)
        params['users'] = users
        reply = await self.rpc(msg)
        return self._map(reply, AddUser)



    #@ReturnMapping(MacaroonResults)
    async def CreateLocalLoginMacaroon(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~MacaroonResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='CreateLocalLoginMacaroon', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, CreateLocalLoginMacaroon)



    #@ReturnMapping(ErrorResults)
    async def DisableUser(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='DisableUser', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, DisableUser)



    #@ReturnMapping(ErrorResults)
    async def EnableUser(self, entities):
        '''
        entities : typing.Sequence[~Entity]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='EnableUser', Version=1, Params=params)
        params['Entities'] = entities
        reply = await self.rpc(msg)
        return self._map(reply, EnableUser)



    #@ReturnMapping(ErrorResults)
    async def SetPassword(self, changes):
        '''
        changes : typing.Sequence[~EntityPassword]
        Returns -> typing.Sequence[~ErrorResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='SetPassword', Version=1, Params=params)
        params['Changes'] = changes
        reply = await self.rpc(msg)
        return self._map(reply, SetPassword)



    #@ReturnMapping(UserInfoResults)
    async def UserInfo(self, entities, include_disabled):
        '''
        entities : typing.Sequence[~Entity]
        include_disabled : bool
        Returns -> typing.Sequence[~UserInfoResult]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='UserManager', Request='UserInfo', Version=1, Params=params)
        params['entities'] = entities
        params['include-disabled'] = include_disabled
        reply = await self.rpc(msg)
        return self._map(reply, UserInfo)


class VolumeAttachmentsWatcher(Type):
    name = 'VolumeAttachmentsWatcher'
    version = 2
    schema =     {'definitions': {'Error': {'additionalProperties': False,
                               'properties': {'Code': {'type': 'string'},
                                              'Info': {'$ref': '#/definitions/ErrorInfo'},
                                              'Message': {'type': 'string'}},
                               'required': ['Message', 'Code'],
                               'type': 'object'},
                     'ErrorInfo': {'additionalProperties': False,
                                   'properties': {'Macaroon': {'$ref': '#/definitions/Macaroon'},
                                                  'MacaroonPath': {'type': 'string'}},
                                   'type': 'object'},
                     'Macaroon': {'additionalProperties': False,
                                  'properties': {'caveats': {'items': {'$ref': '#/definitions/caveat'},
                                                             'type': 'array'},
                                                 'data': {'items': {'type': 'integer'},
                                                          'type': 'array'},
                                                 'id': {'$ref': '#/definitions/packet'},
                                                 'location': {'$ref': '#/definitions/packet'},
                                                 'sig': {'items': {'type': 'integer'},
                                                         'type': 'array'}},
                                  'required': ['data',
                                               'location',
                                               'id',
                                               'caveats',
                                               'sig'],
                                  'type': 'object'},
                     'MachineStorageId': {'additionalProperties': False,
                                          'properties': {'attachmenttag': {'type': 'string'},
                                                         'machinetag': {'type': 'string'}},
                                          'required': ['machinetag',
                                                       'attachmenttag'],
                                          'type': 'object'},
                     'MachineStorageIdsWatchResult': {'additionalProperties': False,
                                                      'properties': {'Changes': {'items': {'$ref': '#/definitions/MachineStorageId'},
                                                                                 'type': 'array'},
                                                                     'Error': {'$ref': '#/definitions/Error'},
                                                                     'MachineStorageIdsWatcherId': {'type': 'string'}},
                                                      'required': ['MachineStorageIdsWatcherId',
                                                                   'Changes',
                                                                   'Error'],
                                                      'type': 'object'},
                     'caveat': {'additionalProperties': False,
                                'properties': {'caveatId': {'$ref': '#/definitions/packet'},
                                               'location': {'$ref': '#/definitions/packet'},
                                               'verificationId': {'$ref': '#/definitions/packet'}},
                                'required': ['location',
                                             'caveatId',
                                             'verificationId'],
                                'type': 'object'},
                     'packet': {'additionalProperties': False,
                                'properties': {'headerLen': {'type': 'integer'},
                                               'start': {'type': 'integer'},
                                               'totalLen': {'type': 'integer'}},
                                'required': ['start', 'totalLen', 'headerLen'],
                                'type': 'object'}},
     'properties': {'Next': {'properties': {'Result': {'$ref': '#/definitions/MachineStorageIdsWatchResult'}},
                             'type': 'object'},
                    'Stop': {'type': 'object'}},
     'type': 'object'}
    

    #@ReturnMapping(MachineStorageIdsWatchResult)
    async def Next(self):
        '''

        Returns -> typing.Union[~Error, typing.Sequence[~MachineStorageId]]
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='VolumeAttachmentsWatcher', Request='Next', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Next)



    #@ReturnMapping(None)
    async def Stop(self):
        '''

        Returns -> None
        '''
        # map input types to rpc msg
        params = dict()
        msg = dict(Type='VolumeAttachmentsWatcher', Request='Stop', Version=2, Params=params)

        reply = await self.rpc(msg)
        return self._map(reply, Stop)


