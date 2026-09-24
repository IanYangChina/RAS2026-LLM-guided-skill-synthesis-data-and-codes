## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

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
- Frozen realised-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176062, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176062, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176062, -0.017054623272995572, 0.025)
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
  frozen_targets: {'socket_entry': [0.5296199363176062, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176062, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.903, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176062, -0.017054623272995572, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5296199363176062, -0.017054623272995572, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.319) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_socket_entry
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.5
- id: insertion
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_entry
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_socket_entry
- id: align_to_socket
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_socket_entry
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.095
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.08
      - 0.11
      default: 0.095
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion
- id: insert_peg
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.045
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: add
    insertion_depth:
      type: scalar
      range:
      - 0.025
      - 0.055
      default: 0.045
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: stuck_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion
- id: retreat
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (add)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.095], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_peg** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.045, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (add)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=stuck_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **retreat** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (add)

## Design Metrics

- **Composite score**: 0.319
- **task_score** (E): 0.903
- **fitness_score**: 0.709  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 1.00 | 0.00 | 0.1167 |
| align_to_socket | 1.00 | 0.00 | 0.0094 |
| descend_to_contact | 1.00 | 0.00 | 0.0066 |
| insert_peg | 0.00 | 1.00 | 0.0018 |
| retreat | 1.00 | 0.00 | 0.0405 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.012, 0.188) | (0.504, -0.000, 0.340)→(0.513, -0.012, 0.228) | 0.260→0.151 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_socket | align | 1.00 / step_budget | (0.508, -0.012, 0.188)→(0.509, -0.013, 0.179) | (0.513, -0.012, 0.228)→(0.514, -0.013, 0.219) | 0.151→0.143 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_contact | descend | 1.00 / step_budget | (0.509, -0.013, 0.179)→(0.509, -0.013, 0.176) | (0.514, -0.013, 0.219)→(0.514, -0.013, 0.215) | 0.143→0.140 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_peg | insert | 0.00 / guard_failure | (0.525, -0.003, 0.049)→(0.524, -0.003, 0.048) | (0.514, -0.013, 0.215)→(0.546, -0.011, 0.084) | 0.140→0.049 | 1.00 / 1.667 | 6793.159 | 6802.496 |
| retreat | retract | 1.00 / step_budget | (0.524, -0.003, 0.048)→(0.520, -0.003, 0.088) | (0.545, -0.011, 0.080)→(0.541, -0.011, 0.120) | 0.047→0.060 | 0.00 / 0.000 | 0.000 | 17652.581 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.944
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.944
- phase_score: 0.619
- phase_breakdown.reach_socket_entry_score: 0.543
- phase_breakdown.insertion_score: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.944
- **Median Q (composite search score)**: 0.324
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.345


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ad55441961509110caa3e00662ff00c043a366a9841ef346adcb2ae98eb0fa2d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `848090e975b2909410760ed4539d133eb61635ea5a8640e3622d2871416125a9`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42718,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.04218,"approach_entry.approach_speed":0.07986,"descend_to_contact.descend_offset":0.08185,"insert_peg.insert_speed":0.03621,"insert_peg.insertion_depth":0.037,"retreat.retract_speed":0.06832},"optimized_scores":{"best_composite_score":0.35897,"best_fitness_score":0.74897,"best_task_score":0.94419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":51.0,"contact_point_centroid":[0.52505,-0.0059,0.04647],"force_p95":12247.65523,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12653.56839,"mean_force":2537.9252,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51316,-0.00143,0.0509]},{"body_a":"attachment","body_b":"peg_socket","contact_count":170.0,"contact_point_centroid":[0.5145,0.01298,0.06868],"force_p95":5202.64297,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11803.72016,"mean_force":599.37811,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51288,-0.00158,0.06571]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.53038,-0.00598,0.04772],"force_p95":8145.45398,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8249.85689,"mean_force":7205.82778,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51863,-0.00032,0.05284]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.52101,0.01351,0.0577],"force_p95":6860.60124,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7090.04076,"mean_force":4298.00595,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51962,-0.0006,0.05488]},{"body_a":"attachment","body_b":"peg_socket","contact_count":134.0,"contact_point_centroid":[0.49959,-0.00343,0.073],"force_p95":94.02109,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6142.57262,"mean_force":225.44661,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51278,-0.00165,0.06612]}],"total_contact_groups":5},"final_pose_error":0.01033,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51243,0.00025,0.08907],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":12653.56839,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":391.0,"n_steps_budget":990.0,"object_pos_end":[0.52814,-0.01519,0.22743],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15086,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52356,-0.01519,0.18769],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.53037,-0.01665,0.21639],"object_pos_start":[0.52814,-0.01519,0.22743],"object_to_goal_dist_end":0.14072,"object_to_goal_dist_start":0.15086,"object_z_max":0.22743,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52534,-0.01664,0.17671],"tcp_start":[0.52356,-0.01519,0.18769],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.53056,-0.01686,0.20362],"object_pos_start":[0.53037,-0.01665,0.21639],"object_to_goal_dist_end":0.12845,"object_to_goal_dist_start":0.14072,"object_z_max":0.21639,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.52514,-0.01684,0.16399],"tcp_start":[0.52534,-0.01664,0.17671],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.53705,-0.00896,0.08947],"object_pos_start":[0.53056,-0.01686,0.20362],"object_to_goal_dist_end":0.03928,"object_to_goal_dist_start":0.12845,"object_z_max":0.20362,"peak_contact_force":8249.85689,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":8249.85689,"subtask_id":"insertion","tcp_end":[0.51649,0.00025,0.04857],"tcp_start":[0.5178,-8e-05,0.05114],"tcp_to_object_dist_end":0.0467,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":409.0,"n_steps_budget":600.0,"object_pos_end":[0.53128,-0.00876,0.12318],"object_pos_start":[0.5349,-0.00874,0.08292],"object_to_goal_dist_end":0.05404,"object_to_goal_dist_start":0.0361,"object_z_max":0.12311,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":355.0,"raw_peak_contact_force":12653.56839,"tcp_end":[0.51243,0.00025,0.08907],"tcp_start":[0.51649,0.00025,0.04857],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `86374ae559fdd7367448730b4cd37979be4c5ee1e51a6d45d322ddd67c264ad8`; realized-scene SHA-256: `77fea26f11e91c54ae4a9c1f03cd5e6af1b4f6cac3191aa4cbd28ae81b548c93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95082,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.03437,"approach_entry.approach_speed":0.11136,"descend_to_contact.descend_offset":0.10732,"insert_peg.insert_speed":0.04568,"insert_peg.insertion_depth":0.03969,"retreat.retract_speed":0.02168},"optimized_scores":{"best_composite_score":0.3237,"best_fitness_score":0.7137,"best_task_score":0.92812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.52606,-0.01405,0.04397],"force_p95":32137.45728,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33657.94563,"mean_force":16135.81717,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51632,-0.0072,0.047]},{"body_a":"attachment","body_b":"peg_socket","contact_count":499.0,"contact_point_centroid":[0.50633,-0.01358,0.0724],"force_p95":93.947,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24186.62003,"mean_force":688.4054,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51916,-0.01011,0.066]},{"body_a":"attachment","body_b":"peg_socket","contact_count":17.0,"contact_point_centroid":[0.51583,0.00704,0.05041],"force_p95":12768.55692,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13524.83041,"mean_force":9731.72455,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51456,-0.00613,0.04453]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.52847,-0.01702,0.04634],"force_p95":10993.66854,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11266.54244,"mean_force":7220.47052,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51886,-0.00996,0.05177]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.50568,-0.01241,0.05672],"force_p95":9884.6797,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10028.25447,"mean_force":8592.50672,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51791,-0.00931,0.04999]}],"total_contact_groups":5},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51257,-0.00755,0.0871],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":33657.94563,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":398.0,"n_steps_budget":750.0,"object_pos_end":[0.53438,-0.02096,0.2266],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15203,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52978,-0.02095,0.18687],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.53742,-0.023,0.2153],"object_pos_start":[0.53438,-0.02096,0.2266],"object_to_goal_dist_end":0.14226,"object_to_goal_dist_start":0.15203,"object_z_max":0.2266,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.53234,-0.02298,0.17563],"tcp_start":[0.52978,-0.02095,0.18687],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.53835,-0.02329,0.22011],"object_pos_start":[0.53742,-0.023,0.2153],"object_to_goal_dist_end":0.14712,"object_to_goal_dist_start":0.14226,"object_z_max":0.22009,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.53278,-0.02327,0.1805],"tcp_start":[0.53234,-0.02298,0.17563],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.53829,-0.02418,0.08324],"object_pos_start":[0.53835,-0.02329,0.22011],"object_to_goal_dist_end":0.0454,"object_to_goal_dist_start":0.14712,"object_z_max":0.22011,"peak_contact_force":11266.54244,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":11266.54244,"subtask_id":"insertion","tcp_end":[0.51602,-0.00785,0.04643],"tcp_start":[0.51714,-0.00875,0.04853],"tcp_to_object_dist_end":0.04602,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.53315,-0.02284,0.1178],"object_pos_start":[0.53628,-0.02308,0.07737],"object_to_goal_dist_end":0.05522,"object_to_goal_dist_start":0.04308,"object_z_max":0.11774,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":541.0,"raw_peak_contact_force":33657.94563,"tcp_end":[0.51257,-0.00755,0.0871],"tcp_start":[0.51602,-0.00785,0.04643],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `caf3f4690e3f1b09696902a0a7669c72f02512d93a4ac4443caef9efffcf46f7`; realized-scene SHA-256: `6cd5caaafe0ec0cc23a4551cd60416799cdbf9885c1214f7b258fb3313892a60`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.31008,"average_mean_iterations":64.10853,"average_solve_count":129.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.03212,"approach_entry.approach_speed":0.14149,"descend_to_contact.descend_offset":0.10262,"insert_peg.insert_speed":0.03478,"insert_peg.insertion_depth":0.0362,"retreat.retract_speed":0.07601},"optimized_scores":{"best_composite_score":0.27458,"best_fitness_score":0.66458,"best_task_score":0.83525},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":24.0,"contact_point_centroid":[0.55178,-0.00046,-0.00231],"force_p95":6601.54155,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6646.22905,"mean_force":4084.88017,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.53994,-0.00053,0.00457]},{"body_a":"attachment","body_b":"peg_socket","contact_count":66.0,"contact_point_centroid":[0.52982,-0.00015,0.03349],"force_p95":6382.65865,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6553.38019,"mean_force":1591.69019,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54138,-0.00034,0.02457]},{"body_a":"attachment","body_b":"peg_socket","contact_count":250.0,"contact_point_centroid":[0.53022,-9e-05,0.0667],"force_p95":104.72,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1685.82959,"mean_force":99.94209,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54243,-0.00018,0.05808]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52946,1e-05,0.06149],"force_p95":891.08738,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":891.08738,"mean_force":891.08738,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.54086,-4e-05,0.05281]}],"total_contact_groups":4},"final_pose_error":0.01088,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.53581,-0.00021,0.08823],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":6646.22905,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":335.0,"n_steps_budget":600.0,"object_pos_end":[0.47567,-6e-05,0.22962],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15158,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.47112,-7e-05,0.18988],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.47411,-7e-05,0.22455],"object_pos_start":[0.47567,-6e-05,0.22962],"object_to_goal_dist_end":0.14685,"object_to_goal_dist_start":0.15158,"object_z_max":0.22962,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.46933,-8e-05,0.18483],"tcp_start":[0.47112,-7e-05,0.18988],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.4732,-7e-05,0.22271],"object_pos_start":[0.47411,-7e-05,0.22455],"object_to_goal_dist_end":0.1452,"object_to_goal_dist_start":0.14685,"object_z_max":0.22455,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.46826,-8e-05,0.18302],"tcp_start":[0.46933,-8e-05,0.18483],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.56329,0.00017,0.08072],"object_pos_start":[0.4732,-7e-05,0.22271],"object_to_goal_dist_end":0.06329,"object_to_goal_dist_start":0.1452,"object_z_max":0.22271,"peak_contact_force":863.07623,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":891.08738,"subtask_id":"insertion","tcp_end":[0.53976,-8e-05,0.04837],"tcp_start":[0.53976,-8e-05,0.04837],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55975,5e-05,0.12028],"object_pos_start":[0.56329,0.00017,0.08072],"object_to_goal_dist_end":0.07206,"object_to_goal_dist_start":0.06329,"object_z_max":0.12021,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":340.0,"raw_peak_contact_force":6646.22905,"tcp_end":[0.53581,-0.00021,0.08823],"tcp_start":[0.53976,-8e-05,0.04837],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```