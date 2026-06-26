from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Annotated


class Suggestion(BaseModel):
    form_section: Annotated[Literal["GeneralInfo", "ComputeDetails"], Field(
        description="Section of the form the field belongs to")]
    field_name: Annotated[str, Field(description="Key of a field in the form")]
    current_value: Annotated[Optional[str], Field(
        description="Value of the field currently present in the CiDeR database (Use 'None' if missing)")]
    proposed_value: Annotated[Optional[str], Field(
        description="Value based on the documentation to replace the current value in the database")]
    reasoning: Annotated[Optional[str], Field(
        description="Explanation on why this change is needed. Include excerpt related to the suggestion")]


class AuditReport(BaseModel):
    audit_summary: Annotated[str, Field(
        description="Summary on the audit and suggestions for modification")]
    modifications: Annotated[List[Suggestion], Field(
        description="List of suggestions for modification of CiDeR records to keep it up-to-date with the documenation")]


# Form fields

class GeneralInfo(BaseModel):
    descriptive_name: Annotated[str, Field(
        description="Descriptive Name of the resource")]
    short_name: Annotated[str, Field(description="Short name of the resource")]
    global_resource_id: Annotated[Optional[str], Field(
        description="Resource id, also defined as info_resource_id")]
    organizations: Annotated[List[str], Field(
        description="Organizations the resource is associated with")]
    infrastructure_type: Annotated[Optional[str], Field(
        description="Type of the resource (Compute/Storage/Gateway)")]
    description: Annotated[Optional[str], Field(
        description="Description about the resource")]
    recommended_use: Annotated[Optional[str], Field(
        description="Recommendation on how the resource should be used")]
    latitude: Annotated[Optional[str], Field(
        description="Latitude of location of the resource")]
    longitude: Annotated[Optional[str], Field(
        description="Longitude of location of the resource")]
    user_guide_url: Annotated[Optional[str], Field(
        description="URL of the User Guide documentation of the resource")]
    internal_only: Annotated[Optional[bool], Field(
        description="Is this resource an internal only ACCESS infrastructure?")]


class ComputeDetails(BaseModel):
    platform_name: Annotated[Optional[str], Field(description="Platform Name")]
    login_hostname: Annotated[Optional[str],
                              Field(description="Login Hostname")]
    alternate_login_hostname: Annotated[Optional[str], Field(
        description="Alternate Login Hostname")]
    job_manager: Annotated[Optional[str], Field(description="Job Manager")]
    batch_system: Annotated[Optional[str], Field(description="Batch System")]
    manufacturer: Annotated[Optional[str], Field(description="Manufacturer")]
    model: Annotated[Optional[str], Field(description="Model")]
    operating_system: Annotated[Optional[str],
                                Field(description="Operating System")]
    node_count: Annotated[Optional[str], Field(description="Node Count")]
    cpu_core_count_per_node: Annotated[Optional[str], Field(
        description="CPU Core Count per Node")]
    cpu_type: Annotated[Optional[str], Field(description="CPU Type")]
    memory_per_cpu_in_gb: Annotated[Optional[str],
                                    Field(description="Memory per CPU in GB")]
    cpu_speed_in_ghz: Annotated[Optional[str],
                                Field(description="CPU Speed in GHz")]
    local_storage_per_node_in_gb: Annotated[Optional[str], Field(
        description="Local Storage per Node in GB")]
    gb_of_primary_storage_shared: Annotated[Optional[str], Field(
        description="GB of Primary Storage Shared")]
    peak_teraflops: Annotated[Optional[str],
                              Field(description="Peak Teraflops")]
    rmax: Annotated[Optional[str], Field(description="RMAX")]
    rpeak: Annotated[Optional[str], Field(description="RPEAK")]
    interconnect: Annotated[Optional[str], Field(description="Interconnect")]
    nfs_network: Annotated[Optional[str], Field(description="NFS Network")]
    storage_network: Annotated[Optional[str],
                               Field(description="Storage Network")]
    gpu_description: Annotated[Optional[str],
                               Field(description="GPU Description")]
    graphics_card_description: Annotated[Optional[str], Field(
        description="Graphics Card Description")]
    max_reservable_su: Annotated[Optional[str],
                                 Field(description="Max Reservable SU")]
    ip_address: Annotated[Optional[str], Field(description="IP Address")]
    gateway_recommended_use: Annotated[Optional[str], Field(
        description="Gateway Recommended Use")]
    # dropdown option should be Literal or Enum with all options
    machine_type: Annotated[Optional[str], Field(description="Machine Type")]
