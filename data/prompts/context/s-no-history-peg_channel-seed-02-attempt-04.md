## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.490) — your mutation base

```yaml
skill: peg_channel_new
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.02
  weight: 0.3
- id: push_complete
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    descend_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.01
    - 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    contact_offset_y:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: add
    contact_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: add
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_contact
- id: push_phase
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.026
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    retry_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_complete
- id: retract_tcp
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - descend_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - contact_offset_y: status=consumed; consumers=target.offset.y (add)
    - contact_offset_z: status=consumed; consumers=target.offset.z (add)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.026], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.490
- **task_score** (E): 0.278
- **fitness_score**: 0.450  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0320 |
| descend_to_peg | 1.00 | 1.00 | 0.1709 |
| contact_peg | 0.33 | 1.00 | 0.0982 |
| push_phase | 1.00 | 1.00 | 0.1525 |
| retract_tcp | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.186, 0.276) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.033) | 0.151→0.148 | 1.00 / 1.000 | 0.762 | 3.659 |
| descend_to_peg | descend | 1.00 / step_budget | (0.499, 0.186, 0.276)→(0.497, 0.178, 0.106) | (0.498, 0.068, 0.033)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 0.714 |
| contact_peg | contact | 0.33 / step_budget | (0.497, 0.178, 0.106)→(0.502, 0.097, 0.053) | (0.498, 0.068, 0.034)→(0.498, 0.067, 0.035) | 0.148→0.147 | 1.00 / 1.667 | 4.426 | 4.755 |
| push_phase | push | 1.00 / time_limit | (0.502, 0.097, 0.053)→(0.506, -0.054, 0.032) | (0.498, 0.067, 0.035)→(0.494, -0.050, 0.028) | 0.147→0.036 | 1.00 / 3.333 | 132.253 | 163.241 |
| retract_tcp | retract | 1.00 / step_budget | (0.506, -0.054, 0.032)→(0.502, -0.053, 0.073) | (0.494, -0.050, 0.028)→(0.501, -0.048, 0.033) | 0.036→0.037 | 1.00 / 1.333 | 3.263 | 85.813 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.883
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.546
- phase_score: 0.577
- phase_breakdown.push_complete_score: 0.554
- phase_breakdown.reach_contact_score: 0.631

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.565
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: -0.471
- **K-run variance**: 0.0105
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.296


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61871,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00445,"approach_peg.approach_offset_y":0.04782,"approach_peg.approach_offset_z":0.12376,"approach_peg.pose_tolerance":0.0286,"contact_peg.approach_offset_x":0.01122,"contact_peg.contact_offset_y":0.01689,"contact_peg.contact_offset_z":0.01209,"contact_peg.force_threshold":10.35711,"descend_to_peg.approach_offset_x":-0.00277,"descend_to_peg.approach_offset_y":0.06145,"descend_to_peg.descend_offset_z":0.02313,"descend_to_peg.pose_tolerance":0.02496,"push_phase.max_time":10.58117,"push_phase.push_distance":0.18124,"push_phase.push_speed":0.09689,"push_phase.retry_offset_x":-0.00196,"push_phase.retry_offset_y":-0.00124},"optimized_scores":{"best_composite_score":-0.37522,"best_fitness_score":0.56478,"best_task_score":0.54586},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.55502,-0.1,0.06499],"force_p95":153.34206,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.54801,"mean_force":103.75384,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49965,-0.05021,0.0254]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53403,-0.03746,0.05999],"force_p95":71.4158,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.92307,"mean_force":44.53154,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49796,-0.04399,0.02515]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55444,-0.1,0.06497],"force_p95":62.50684,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.97283,"mean_force":52.8421,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50102,-0.0543,0.02568]},{"body_a":"attachment","body_b":"peg","contact_count":649.0,"contact_point_centroid":[0.49653,-0.00327,0.0331],"force_p95":8.12149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.83701,"mean_force":2.01303,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49785,0.00856,0.03272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.495,-0.10022,0.03345],"force_p95":42.14164,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.84539,"mean_force":10.75608,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50061,-0.05315,0.02563]},{"body_a":"attachment","body_b":"peg","contact_count":430.0,"contact_point_centroid":[0.49612,-0.06447,0.04719],"force_p95":13.14057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.89474,"mean_force":10.04625,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49745,-0.05276,0.04702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":444.0,"contact_point_centroid":[0.49283,-0.10034,0.05891],"force_p95":12.79209,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.91145,"mean_force":9.59612,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49752,-0.0528,0.04643]},{"body_a":"peg","body_b":"channel_base_body","contact_count":831.0,"contact_point_centroid":[0.49523,-0.02282,0.00982],"force_p95":5.92918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.63911,"mean_force":1.62618,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49792,0.01316,0.03346]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":223.0,"contact_point_centroid":[0.47491,-0.08207,0.05361],"force_p95":6.52132,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.62502,"mean_force":1.599,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49763,-0.05293,0.04323]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":213.0,"contact_point_centroid":[0.47482,0.02672,0.02999],"force_p95":3.26133,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.49611,"mean_force":0.726,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49779,0.0562,0.03955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.47853,-0.08158,0.00985],"force_p95":4.93665,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.11628,"mean_force":2.37795,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50092,-0.05428,0.02589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50879,0.06609,0.00903],"force_p95":2.08876,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.97195,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49459,0.18751,0.28616]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49839,0.19673,0.29656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.49459,0.06383,0.00937],"force_p95":0.5824,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71366,"mean_force":0.54529,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49099,0.17889,0.19202]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.49508,0.06388,0.0094],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.5456,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49401,0.13564,0.07331]}],"total_contact_groups":15},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49555,-0.07739,0.04953],"final_tcp_position":[0.49737,-0.05235,0.06657],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":204.54801,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":47.0,"n_steps_budget":600.0,"object_pos_end":[0.49489,0.06388,0.03329],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.75051,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":48.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.49277,0.18286,0.28121],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.49505,0.0637,0.03392],"object_pos_start":[0.49489,0.06388,0.03329],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14412,"object_z_max":0.03392,"peak_contact_force":0.54721,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":290.0,"raw_peak_contact_force":0.71366,"subtask_id":"reach_contact","tcp_end":[0.48985,0.17547,0.10083],"tcp_start":[0.49277,0.18286,0.28121],"tcp_to_object_dist_end":0.13037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.495,0.06362,0.034],"object_pos_start":[0.49505,0.0637,0.03392],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14392,"object_z_max":0.034,"peak_contact_force":0.54384,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":572.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_contact","tcp_end":[0.50137,0.09549,0.0495],"tcp_start":[0.48985,0.17547,0.10083],"tcp_to_object_dist_end":0.03601,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49507,-0.08303,0.03454],"object_pos_start":[0.495,0.06362,0.034],"object_to_goal_dist_end":0.00796,"object_to_goal_dist_start":0.14384,"object_z_max":0.03643,"peak_contact_force":133.27346,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1817.0,"raw_peak_contact_force":204.54801,"subtask_id":"push_complete","tcp_end":[0.50097,-0.05426,0.02566],"tcp_start":[0.50137,0.09549,0.0495],"tcp_to_object_dist_end":0.03069,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.49555,-0.07739,0.04953],"object_pos_start":[0.49507,-0.08303,0.03454],"object_to_goal_dist_end":0.01084,"object_to_goal_dist_start":0.00796,"object_z_max":0.04949,"peak_contact_force":8.42225,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1111.0,"raw_peak_contact_force":63.97283,"tcp_end":[0.49737,-0.05235,0.06657],"tcp_start":[0.50097,-0.05426,0.02566],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69444,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00341,"approach_peg.approach_offset_y":0.04055,"approach_peg.approach_offset_z":0.13378,"approach_peg.pose_tolerance":0.03917,"contact_peg.approach_offset_x":0.01114,"contact_peg.contact_offset_y":0.00818,"contact_peg.contact_offset_z":0.01464,"contact_peg.force_threshold":20.49297,"descend_to_peg.approach_offset_x":0.00298,"descend_to_peg.approach_offset_y":0.06952,"descend_to_peg.descend_offset_z":0.01997,"descend_to_peg.pose_tolerance":0.02024,"push_phase.max_time":9.7338,"push_phase.push_distance":0.1705,"push_phase.push_speed":0.09871,"push_phase.retry_offset_x":-0.00505,"push_phase.retry_offset_y":-0.00258},"optimized_scores":{"best_composite_score":-0.47087,"best_fitness_score":0.46913,"best_task_score":0.13001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.493,-0.01116,0.00776],"force_p95":155.32677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.15319,"mean_force":57.8504,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50163,0.00454,0.03893]},{"body_a":"attachment","body_b":"peg","contact_count":987.0,"contact_point_centroid":[0.4964,-0.00354,0.04057],"force_p95":154.08159,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.2684,"mean_force":61.77641,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50165,0.00378,0.03882]},{"body_a":"peg","body_b":"channel_base_body","contact_count":374.0,"contact_point_centroid":[0.50026,-0.0542,0.00838],"force_p95":49.30798,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.53624,"mean_force":6.62676,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50604,-0.07452,0.05539]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.49727,-0.07494,0.0414],"force_p95":73.83148,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.34483,"mean_force":28.43602,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50872,-0.07503,0.03868]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":76.0,"contact_point_centroid":[0.47456,-0.06283,0.02574],"force_p95":44.10893,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.22067,"mean_force":18.70629,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50856,-0.07498,0.03932]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":893.0,"contact_point_centroid":[0.47483,-0.00056,0.02521],"force_p95":27.35384,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.16728,"mean_force":14.04147,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50132,0.01054,0.03959]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49774,0.07416,0.05264],"force_p95":12.70593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.16161,"mean_force":6.46134,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50034,0.08572,0.05226]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52514,-0.04883,0.02504],"force_p95":10.66424,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.75615,"mean_force":5.50547,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.5051,-0.07436,0.06532]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.49397,0.05799,0.0094],"force_p95":0.55183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.53688,"mean_force":0.69745,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4953,0.13036,0.06966]},{"body_a":"peg","body_b":"world","contact_count":69.0,"contact_point_centroid":[0.49254,-0.0315,-0.00041],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68335,"mean_force":0.24234,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5009,-0.03351,0.03269]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47475,0.05391,0.05999],"force_p95":5.68168,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.71133,"mean_force":2.63826,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5006,0.08373,0.0515]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50617,0.0589,0.00902],"force_p95":3.90188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":2.12378,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48999,0.18387,0.28965]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49565,0.19336,0.29574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.49429,0.05905,0.00935],"force_p95":0.56835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86145,"mean_force":0.54737,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49003,0.17873,0.19042]}],"total_contact_groups":14},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50516,-0.05103,0.02406],"final_tcp_position":[0.50517,-0.07437,0.07393],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":163.15319,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.49386,0.05894,0.03257],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.9856,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":44.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.4881,0.18055,0.28767],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05901,0.03385],"object_pos_start":[0.49386,0.05894,0.03257],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.13928,"object_z_max":0.03385,"peak_contact_force":0.54427,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":369.0,"raw_peak_contact_force":0.86145,"subtask_id":"reach_contact","tcp_end":[0.49315,0.1777,0.09219],"tcp_start":[0.4881,0.18055,0.28767],"tcp_to_object_dist_end":0.13226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.49333,0.05594,0.0364],"object_pos_start":[0.49403,0.05901,0.03385],"object_to_goal_dist_end":0.13615,"object_to_goal_dist_start":0.13927,"object_z_max":0.03638,"peak_contact_force":12.18904,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":666.0,"raw_peak_contact_force":13.16161,"subtask_id":"reach_contact","tcp_end":[0.50078,0.08278,0.05118],"tcp_start":[0.49315,0.1777,0.09219],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49256,-0.05133,0.02343],"object_pos_start":[0.49333,0.05594,0.0364],"object_to_goal_dist_end":0.03394,"object_to_goal_dist_start":0.13615,"object_z_max":0.04002,"peak_contact_force":154.0889,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2946.0,"raw_peak_contact_force":163.15319,"subtask_id":"push_complete","tcp_end":[0.50879,-0.07485,0.03321],"tcp_start":[0.50078,0.08278,0.05118],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":374.0,"n_steps_budget":600.0,"object_pos_end":[0.50516,-0.05103,0.02406],"object_pos_start":[0.49256,-0.05133,0.02343],"object_to_goal_dist_end":0.03347,"object_to_goal_dist_start":0.03394,"object_z_max":0.02744,"peak_contact_force":0.72915,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":550.0,"raw_peak_contact_force":105.53624,"tcp_end":[0.50517,-0.07437,0.07393],"tcp_start":[0.50879,-0.07485,0.03321],"tcp_to_object_dist_end":0.05506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74627,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.0046,"approach_peg.approach_offset_y":0.05554,"approach_peg.approach_offset_z":0.08453,"approach_peg.pose_tolerance":0.03922,"contact_peg.approach_offset_x":0.001,"contact_peg.contact_offset_y":0.01859,"contact_peg.contact_offset_z":0.01979,"contact_peg.force_threshold":10.8911,"descend_to_peg.approach_offset_x":-0.00198,"descend_to_peg.approach_offset_y":0.0474,"descend_to_peg.descend_offset_z":0.02069,"descend_to_peg.pose_tolerance":0.04999,"push_phase.max_time":11.82206,"push_phase.push_distance":0.15459,"push_phase.push_speed":0.09572,"push_phase.retry_offset_x":-0.00023,"push_phase.retry_offset_y":-0.00528},"optimized_scores":{"best_composite_score":-0.62434,"best_fitness_score":0.31566,"best_task_score":0.15845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":962.0,"contact_point_centroid":[0.50295,0.02086,0.00846],"force_p95":113.04412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.02181,"mean_force":43.60983,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.502,0.0414,0.04377]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.50254,0.0277,0.04373],"force_p95":112.03161,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.86783,"mean_force":48.06942,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50205,0.03788,0.04319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":389.0,"contact_point_centroid":[0.50124,-0.01875,0.00831],"force_p95":29.28977,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.92885,"mean_force":3.55296,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50503,-0.03181,0.05827]},{"body_a":"attachment","body_b":"peg","contact_count":54.0,"contact_point_centroid":[0.49916,-0.04039,0.04289],"force_p95":54.38602,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.08983,"mean_force":21.51138,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50746,-0.03216,0.04053]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":59.0,"contact_point_centroid":[0.47481,0.00722,0.02664],"force_p95":21.40928,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.35093,"mean_force":6.92203,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50737,-0.03214,0.04086]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":145.0,"contact_point_centroid":[0.47497,0.01466,0.02424],"force_p95":13.68526,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.30642,"mean_force":7.4717,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50585,-0.01597,0.03746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":283.0,"contact_point_centroid":[0.52505,0.04769,0.03997],"force_p95":13.97182,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.7003,"mean_force":9.24515,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50057,0.07423,0.04804]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52504,-0.03908,0.02427],"force_p95":7.85189,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.85915,"mean_force":2.55908,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50436,-0.03172,0.06355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50019,0.08118,0.00903],"force_p95":3.36344,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":1.10648,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5108,0.19524,0.27159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5036,0.19854,0.29131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50621,0.08091,0.00936],"force_p95":0.56046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56764,"mean_force":0.54342,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51167,0.18771,0.19475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50595,0.08083,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55176,"mean_force":0.54677,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50344,0.1477,0.08827]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50364,-0.01592,0.0241],"final_tcp_position":[0.50445,-0.03172,0.07767],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":122.02181,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.08088,0.03335],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5495,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":64.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.51515,0.1931,0.25954],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.506,0.08088,0.03335],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54734,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":124.0,"raw_peak_contact_force":0.56764,"subtask_id":"reach_contact","tcp_end":[0.50709,0.18204,0.12375],"tcp_start":[0.51515,0.1931,0.25954],"tcp_to_object_dist_end":0.1354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":572.0,"raw_peak_contact_force":0.55176,"subtask_id":"reach_contact","tcp_end":[0.50321,0.1134,0.05795],"tcp_start":[0.50709,0.18204,0.12375],"tcp_to_object_dist_end":0.04061,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,-0.01607,0.02536],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.06577,"object_to_goal_dist_start":0.16112,"object_z_max":0.04005,"peak_contact_force":109.39795,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2270.0,"raw_peak_contact_force":122.02181,"subtask_id":"push_complete","tcp_end":[0.50805,-0.03192,0.03694],"tcp_start":[0.50321,0.1134,0.05795],"tcp_to_object_dist_end":0.02352,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":600.0,"object_pos_end":[0.50364,-0.01592,0.0241],"object_pos_start":[0.4951,-0.01607,0.02536],"object_to_goal_dist_end":0.06613,"object_to_goal_dist_start":0.06577,"object_z_max":0.02734,"peak_contact_force":0.63675,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":512.0,"raw_peak_contact_force":87.92885,"tcp_end":[0.50445,-0.03172,0.07767],"tcp_start":[0.50805,-0.03192,0.03694],"tcp_to_object_dist_end":0.05586,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```