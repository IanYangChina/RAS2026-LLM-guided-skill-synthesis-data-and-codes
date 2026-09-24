## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → approach → descend → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1036 | 0.86 | ✅ accepted |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2486 | 0.86 | ✅ accepted |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.104) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_to_socket
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
- id: approach_socket
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.09
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.arc_height
        mode: replace
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.06
      - 0.1
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
- id: contact_entry
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.07
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: insert_depth
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
- id: retract_from_hole
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.09]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_depth** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.104
- **task_score** (E): 0.861
- **fitness_score**: 0.407  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.33 | 1.00 | 0.1034 |
| approach_socket | 0.33 | 1.00 | 0.0187 |
| descend_to_entry | 0.00 | 0.67 | 0.0003 |
| contact_entry | 1.00 | 1.00 | 0.0018 |
| insert_depth | 0.00 | 0.33 | 0.0515 |
| retract_from_hole | 0.33 | 1.00 | 0.0371 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.529, 0.008, 0.246) | (0.504, -0.000, 0.340)→(0.551, -0.001, 0.218) | 0.260→0.147 | 1.00 / 1.667 | 247.338 | 3291.172 |
| approach_socket | approach | 0.33 / step_budget | (0.529, 0.008, 0.246)→(0.536, 0.001, 0.261) | (0.551, -0.001, 0.218)→(0.558, -0.002, 0.231) | 0.147→0.163 | 1.00 / 1.333 | 343.749 | 698.709 |
| descend_to_entry | descend | 0.00 / guard_failure | (0.536, 0.001, 0.261)→(0.536, 0.001, 0.261) | (0.558, -0.002, 0.231)→(0.558, -0.002, 0.232) | 0.163→0.163 | 0.67 / 0.667 | 78.598 | 498.230 |
| contact_entry | contact | 1.00 / force_exceeded | (0.536, 0.001, 0.261)→(0.537, -0.000, 0.262) | (0.558, -0.002, 0.232)→(0.558, -0.003, 0.233) | 0.163→0.164 | 1.00 / 1.000 | 257.140 | 299.981 |
| insert_depth | insert | 0.00 / step_budget | (0.537, -0.000, 0.262)→(0.519, -0.021, 0.275) | (0.558, -0.003, 0.233)→(0.542, -0.022, 0.244) | 0.164→0.172 | 0.33 / 0.333 | 160.315 | 718.357 |
| retract_from_hole | retract | 0.33 / step_budget | (0.519, -0.021, 0.275)→(0.537, -0.017, 0.247) | (0.542, -0.022, 0.244)→(0.566, -0.019, 0.221) | 0.172→0.158 | 1.00 / 1.000 | 247.209 | 611.782 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.867
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.867
- phase_score: 0.166
- phase_breakdown.contact_score: 0.143
- phase_breakdown.approach_score: 0.101
- phase_breakdown.insert_score: 0.228
- phase_breakdown.align_score: 0.037

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.446
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.867
- **Median Q (composite search score)**: 0.128
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.0069,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01694,"approach_socket.approach_speed":0.11306,"approach_socket.arc_height":0.055,"contact_entry.contact_force":5.504,"descend_to_entry.descend_offset":0.06579,"insert_depth.insertion_depth":0.04242,"retract_from_hole.retract_speed":0.10257},"optimized_scores":{"best_composite_score":0.14311,"best_fitness_score":0.44644,"best_task_score":0.86651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.47041,-0.00206,0.07907],"force_p95":1056.06738,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.0877,"mean_force":310.29745,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46009,-0.00206,0.09053]},{"body_a":"peg_socket","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.57685,-0.00532,0.07923],"force_p95":551.05889,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":879.99236,"mean_force":267.63273,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46843,-0.00363,0.14055]},{"body_a":"peg_socket","body_b":"link6","contact_count":898.0,"contact_point_centroid":[0.57872,-0.06657,0.07988],"force_p95":546.20789,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":771.11604,"mean_force":358.52178,"phase_index":5.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.54853,-0.02219,0.32534]},{"body_a":"peg_socket","body_b":"link6","contact_count":716.0,"contact_point_centroid":[0.58953,-0.01078,0.07982],"force_p95":380.1374,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":761.43626,"mean_force":264.75065,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4691,0.00165,0.18148]},{"body_a":"peg_socket","body_b":"link6","contact_count":947.0,"contact_point_centroid":[0.58187,-0.01279,0.07988],"force_p95":571.85495,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":696.519,"mean_force":407.10397,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.51202,-0.03529,0.33631]},{"body_a":"peg_socket","body_b":"link6","contact_count":308.0,"contact_point_centroid":[0.5514,-0.06417,0.07985],"force_p95":382.40072,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":605.90349,"mean_force":256.23879,"phase_index":5.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53492,-0.0276,0.33065]},{"body_a":"peg_socket","body_b":"link6","contact_count":882.0,"contact_point_centroid":[0.58657,-0.00285,0.0799],"force_p95":425.12756,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.62289,"mean_force":352.0943,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.56534,0.02249,0.34199]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.55119,0.01337,0.07884],"force_p95":20.12519,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.50378,"mean_force":20.12519,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45448,-0.00236,0.09777]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.02969,0.08],"force_p95":304.30462,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.30462,"mean_force":304.30462,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.57017,0.00461,0.33402]},{"body_a":"peg_socket","body_b":"link6","contact_count":232.0,"contact_point_centroid":[0.53269,-0.04706,0.07991],"force_p95":176.18695,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.08706,"mean_force":109.94858,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.5138,-0.03609,0.33376]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58961,-0.03504,0.07994],"force_p95":206.86909,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.86909,"mean_force":206.86909,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.56981,0.00697,0.33166]}],"total_contact_groups":11},"final_pose_error":0.18356,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.55875,-0.02626,0.306],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1088.0877,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.57657,0.00301,0.27729],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21165,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":223.77177,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":821.0,"raw_peak_contact_force":1088.0877,"tcp_end":[0.56277,0.01581,0.31258],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58431,0.00393,0.2945],"object_pos_start":[0.57657,0.00301,0.27729],"object_to_goal_dist_end":0.23051,"object_to_goal_dist_start":0.21165,"object_z_max":0.30953,"peak_contact_force":346.71999,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":882.0,"raw_peak_contact_force":564.62289,"tcp_end":[0.56981,0.00697,0.33166],"tcp_start":[0.56277,0.01581,0.31258],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58436,0.00368,0.29479],"object_pos_start":[0.58431,0.00393,0.2945],"object_to_goal_dist_end":0.23079,"object_to_goal_dist_start":0.23051,"object_z_max":0.2945,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":206.86909,"tcp_end":[0.56988,0.00668,0.33195],"tcp_start":[0.56981,0.00697,0.33166],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.58357,0.00181,0.29661],"object_pos_start":[0.58436,0.00368,0.29479],"object_to_goal_dist_end":0.23218,"object_to_goal_dist_start":0.23079,"object_z_max":0.29647,"peak_contact_force":304.30462,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":304.30462,"tcp_end":[0.57024,0.00437,0.33424],"tcp_start":[0.56988,0.00668,0.33195],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5476,-0.03049,0.29823],"object_pos_start":[0.58357,0.00181,0.29661],"object_to_goal_dist_end":0.22543,"object_to_goal_dist_start":0.23218,"object_z_max":0.30867,"peak_contact_force":0.0,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1179.0,"raw_peak_contact_force":696.519,"tcp_end":[0.53038,-0.03238,0.33428],"tcp_start":[0.57024,0.00437,0.33424],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58461,-0.02676,0.27549],"object_pos_start":[0.5476,-0.03049,0.29823],"object_to_goal_dist_end":0.21469,"object_to_goal_dist_start":0.22543,"object_z_max":0.29827,"peak_contact_force":309.9839,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1206.0,"raw_peak_contact_force":771.11604,"tcp_end":[0.55875,-0.02626,0.306],"tcp_start":[0.53038,-0.03238,0.33428],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1087,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.00477,"approach_socket.approach_speed":0.10378,"approach_socket.arc_height":0.04612,"contact_entry.contact_force":9.2341,"descend_to_entry.descend_offset":0.06535,"insert_depth.insertion_depth":0.03142,"retract_from_hole.retract_speed":0.1419},"optimized_scores":{"best_composite_score":0.12761,"best_fitness_score":0.43094,"best_task_score":0.86485},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.54607,0.00729,0.07771],"force_p95":820.1143,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":962.19056,"mean_force":203.58822,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45047,-0.0033,0.10246]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47657,-0.00273,0.07975],"force_p95":847.37689,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.09461,"mean_force":420.51776,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45965,-0.0027,0.08943]},{"body_a":"peg_socket","body_b":"link6","contact_count":763.0,"contact_point_centroid":[0.59131,-0.07997,0.07989],"force_p95":559.02538,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":830.77068,"mean_force":376.53017,"phase_index":5.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.54782,-0.042,0.3183]},{"body_a":"peg_socket","body_b":"link6","contact_count":938.0,"contact_point_centroid":[0.5879,-0.02971,0.07988],"force_p95":499.10018,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":687.86966,"mean_force":326.32787,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.51811,-0.05089,0.33573]},{"body_a":"peg_socket","body_b":"link6","contact_count":126.0,"contact_point_centroid":[0.56516,-0.08025,0.0799],"force_p95":293.43616,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":631.98101,"mean_force":159.82875,"phase_index":5.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53666,-0.04406,0.32997]},{"body_a":"peg_socket","body_b":"link6","contact_count":774.0,"contact_point_centroid":[0.59616,-0.01391,0.07981],"force_p95":368.76013,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":619.85719,"mean_force":259.81381,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46961,-0.00387,0.1768]},{"body_a":"peg_socket","body_b":"link6","contact_count":936.0,"contact_point_centroid":[0.59646,-0.05443,0.07994],"force_p95":366.64618,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.18794,"mean_force":276.35099,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.57448,-0.01776,0.33893]},{"body_a":"peg_socket","body_b":"link6","contact_count":603.0,"contact_point_centroid":[0.53509,-0.05455,0.0799],"force_p95":269.59195,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":443.21729,"mean_force":148.26449,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.51036,-0.05475,0.33398]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56673,-0.00335,0.07859],"force_p95":236.58783,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.43544,"mean_force":61.59862,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45056,-0.00332,0.10365]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59643,-0.05701,0.07977],"force_p95":235.79373,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.79373,"mean_force":235.79373,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.5739,-0.00451,0.33037]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59644,-0.05692,0.07981],"force_p95":233.82852,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.82852,"mean_force":233.82852,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.57398,-0.00479,0.33056]},{"body_a":"peg_socket","body_b":"link6","contact_count":277.0,"contact_point_centroid":[0.505,-0.05868,0.07989],"force_p95":99.98003,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.13507,"mean_force":51.67169,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.50344,-0.05889,0.33449]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54644,-0.05347,0.07949],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44943,-0.00312,0.09475]}],"total_contact_groups":13},"final_pose_error":0.16853,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.57101,-0.03664,0.28942],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":962.19056,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.57389,-0.00516,0.27024],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20415,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":233.21056,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":848.0,"raw_peak_contact_force":962.19056,"tcp_end":[0.55895,0.00902,0.30453],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58758,-0.00925,0.29308],"object_pos_start":[0.57389,-0.00516,0.27024],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.20415,"object_z_max":0.3044,"peak_contact_force":366.63239,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":936.0,"raw_peak_contact_force":459.18794,"tcp_end":[0.5739,-0.00451,0.33037],"tcp_start":[0.55895,0.00902,0.30453],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58764,-0.00949,0.29326],"object_pos_start":[0.58758,-0.00925,0.29308],"object_to_goal_dist_end":0.23076,"object_to_goal_dist_start":0.23056,"object_z_max":0.29308,"peak_contact_force":235.79373,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":235.79373,"tcp_end":[0.57398,-0.00479,0.33056],"tcp_start":[0.5739,-0.00451,0.33037],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5877,-0.00981,0.29372],"object_pos_start":[0.58764,-0.00949,0.29326],"object_to_goal_dist_end":0.23123,"object_to_goal_dist_start":0.23076,"object_z_max":0.29326,"peak_contact_force":233.82852,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":233.82852,"tcp_end":[0.57409,-0.00518,0.33105],"tcp_start":[0.57398,-0.00479,0.33056],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55356,-0.04466,0.29725],"object_pos_start":[0.5877,-0.00981,0.29372],"object_to_goal_dist_end":0.22816,"object_to_goal_dist_start":0.23123,"object_z_max":0.30871,"peak_contact_force":480.94371,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1818.0,"raw_peak_contact_force":687.86966,"tcp_end":[0.53614,-0.04616,0.33322],"tcp_start":[0.57409,-0.00518,0.33105],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.59771,-0.03799,0.25967],"object_pos_start":[0.55356,-0.04466,0.29725],"object_to_goal_dist_end":0.20802,"object_to_goal_dist_start":0.22816,"object_z_max":0.29757,"peak_contact_force":233.58264,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":889.0,"raw_peak_contact_force":830.77068,"tcp_end":[0.57101,-0.03664,0.28942],"tcp_start":[0.53614,-0.04616,0.33322],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.02041,"average_mean_iterations":11.65306,"average_solve_count":98.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01961,"approach_socket.approach_speed":0.07984,"approach_socket.arc_height":0.02812,"contact_entry.contact_force":6.40765,"descend_to_entry.descend_offset":0.06391,"insert_depth.insertion_depth":0.02358,"retract_from_hole.retract_speed":0.05974},"optimized_scores":{"best_composite_score":0.04011,"best_fitness_score":0.34345,"best_task_score":0.85067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":515.0,"contact_point_centroid":[0.52964,0.00018,0.07998],"force_p95":104.11613,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7823.2389,"mean_force":212.37162,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46373,0.00013,0.11789]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00405,0.0651],"force_p95":336.14451,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5227.11015,"mean_force":351.4287,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46066,0.00011,0.11396]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43902,0.01018,0.07977],"force_p95":2492.5131,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2554.40336,"mean_force":1290.88482,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43706,-8e-05,0.08377]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68264,0.00059,-0.0001],"force_p95":358.1299,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1072.317,"mean_force":132.83932,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46545,0.00021,0.12033]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68257,0.00061,-0.0001],"force_p95":1052.02752,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1052.02752,"mean_force":1052.02752,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46545,0.00027,0.12045]},{"body_a":"world","body_b":"link6","contact_count":348.0,"contact_point_centroid":[0.68182,-8e-05,-0.00015],"force_p95":392.69829,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":770.68228,"mean_force":223.04646,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.47519,0.00179,0.13707]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53025,-0.00392,0.0641],"force_p95":342.88103,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.16757,"mean_force":285.44042,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46544,0.0002,0.12029]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00389,0.0642],"force_p95":491.67337,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.67337,"mean_force":491.67337,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46545,0.00027,0.12045]},{"body_a":"peg_socket","body_b":"link7","contact_count":117.0,"contact_point_centroid":[0.52995,-0.00374,0.06597],"force_p95":410.24214,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.66406,"mean_force":323.85944,"phase_index":4.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.46512,0.00037,0.12248]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.68269,0.00063,-2e-05],"force_p95":355.38347,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.80953,"mean_force":297.54886,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46588,0.00028,0.12117]},{"body_a":"world","body_b":"link6","contact_count":433.0,"contact_point_centroid":[0.68627,-0.01884,-9e-05],"force_p95":197.92812,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.45799,"mean_force":172.6402,"phase_index":5.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.48561,0.01416,0.14997]},{"body_a":"world","body_b":"link6","contact_count":234.0,"contact_point_centroid":[0.68286,0.00052,-0.0],"force_p95":9.40921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.20431,"mean_force":2.69734,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,0.00013,0.11948]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,0.00017,0.07997],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.4651,0.00012,0.11947]}],"total_contact_groups":13},"final_pose_error":0.02656,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.48158,0.01234,0.14559],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7823.2389,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50271,0.00015,0.10586],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.026,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":285.03135,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1574.0,"raw_peak_contact_force":7823.2389,"tcp_end":[0.4651,0.00012,0.11947],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50299,0.00028,0.10664],"object_pos_start":[0.50271,0.00015,0.10586],"object_to_goal_dist_end":0.02681,"object_to_goal_dist_start":0.026,"object_z_max":0.10665,"peak_contact_force":317.89468,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37.0,"raw_peak_contact_force":1072.317,"tcp_end":[0.46545,0.00027,0.12045],"tcp_start":[0.4651,0.00012,0.11947],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50316,0.00029,0.10681],"object_pos_start":[0.50299,0.00028,0.10664],"object_to_goal_dist_end":0.027,"object_to_goal_dist_start":0.02681,"object_z_max":0.10664,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":1052.02752,"tcp_end":[0.46562,0.00027,0.12062],"tcp_start":[0.46545,0.00027,0.12045],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.50365,0.00031,0.10795],"object_pos_start":[0.50316,0.00029,0.10681],"object_to_goal_dist_end":0.02819,"object_to_goal_dist_start":0.027,"object_z_max":0.10772,"peak_contact_force":233.28819,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":361.80953,"tcp_end":[0.46621,0.00029,0.12203],"tcp_start":[0.46562,0.00027,0.12062],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":453.0,"n_steps_budget":600.0,"object_pos_end":[0.52449,0.0101,0.13636],"object_pos_start":[0.50365,0.00031,0.10795],"object_to_goal_dist_end":0.06227,"object_to_goal_dist_start":0.02819,"object_z_max":0.13568,"peak_contact_force":0.0,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":465.0,"raw_peak_contact_force":770.68228,"tcp_end":[0.49018,0.0154,0.15624],"tcp_start":[0.46621,0.00029,0.12203],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51692,0.00753,0.12747],"object_pos_start":[0.52449,0.0101,0.13636],"object_to_goal_dist_end":0.05095,"object_to_goal_dist_start":0.06227,"object_z_max":0.14381,"peak_contact_force":198.06174,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":433.0,"raw_peak_contact_force":233.45799,"tcp_end":[0.48158,0.01234,0.14559],"tcp_start":[0.49018,0.0154,0.15624],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```