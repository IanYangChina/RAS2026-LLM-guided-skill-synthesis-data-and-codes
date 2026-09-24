## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.315) — your mutation base

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

- **Composite score**: 0.315
- **task_score** (E): 0.899
- **fitness_score**: 0.705  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 1.00 | 0.00 | 0.1167 |
| align_to_socket | 1.00 | 0.00 | 0.0094 |
| descend_to_contact | 1.00 | 0.00 | 0.0069 |
| insert_peg | 0.00 | 1.00 | 0.0019 |
| retreat | 1.00 | 0.00 | 0.0405 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.012, 0.188) | (0.504, -0.000, 0.340)→(0.513, -0.012, 0.228) | 0.260→0.151 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_socket | align | 1.00 / step_budget | (0.508, -0.012, 0.188)→(0.509, -0.013, 0.179) | (0.513, -0.012, 0.228)→(0.514, -0.013, 0.219) | 0.151→0.143 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_contact | descend | 1.00 / step_budget | (0.509, -0.013, 0.179)→(0.508, -0.013, 0.172) | (0.514, -0.013, 0.219)→(0.514, -0.013, 0.212) | 0.143→0.137 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_peg | insert | 0.00 / guard_failure | (0.526, -0.002, 0.053)→(0.526, -0.002, 0.051) | (0.514, -0.013, 0.212)→(0.547, -0.008, 0.089) | 0.137→0.049 | 1.00 / 2.000 | 3938.520 | 5676.770 |
| retreat | retract | 1.00 / step_budget | (0.526, -0.002, 0.051)→(0.522, -0.002, 0.091) | (0.546, -0.008, 0.085)→(0.542, -0.008, 0.125) | 0.047→0.063 | 0.00 / 0.000 | 0.000 | 13177.341 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.943
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.943
- phase_score: 0.618
- phase_breakdown.reach_socket_entry_score: 0.543
- phase_breakdown.insertion_score: 0.693

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.943
- **Median Q (composite search score)**: 0.313
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25234,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.03866,"approach_entry.approach_speed":0.07144,"descend_to_contact.descend_offset":0.08013,"insert_peg.insert_speed":0.04454,"insert_peg.insertion_depth":0.0416,"retreat.retract_speed":0.05261},"optimized_scores":{"best_composite_score":0.35838,"best_fitness_score":0.74838,"best_task_score":0.9434},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":50.0,"contact_point_centroid":[0.52767,-0.00265,0.04599],"force_p95":15923.28995,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16311.90144,"mean_force":6093.72857,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51524,-0.00136,0.04968]},{"body_a":"attachment","body_b":"peg_socket","contact_count":222.0,"contact_point_centroid":[0.51568,0.0131,0.06898],"force_p95":12400.87795,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15439.83097,"mean_force":1354.46145,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.5131,-0.00136,0.06439]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53123,-0.00638,0.04613],"force_p95":10781.4104,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10968.66931,"mean_force":8323.37743,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51986,-0.00016,0.04982]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.52143,0.01367,0.05308],"force_p95":9691.71376,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9895.24747,"mean_force":7001.76335,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.51986,-0.00016,0.04982]},{"body_a":"attachment","body_b":"peg_socket","contact_count":125.0,"contact_point_centroid":[0.49961,-0.00339,0.07234],"force_p95":223.15089,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.93017,"mean_force":76.04261,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51276,-0.00161,0.06538]}],"total_contact_groups":5},"final_pose_error":0.01039,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51287,0.00105,0.08522],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":16311.90144,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.52812,-0.01521,0.22725],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15068,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52353,-0.01521,0.18752],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":115.0,"n_steps_budget":600.0,"object_pos_end":[0.53038,-0.01666,0.21633],"object_pos_start":[0.52812,-0.01521,0.22725],"object_to_goal_dist_end":0.14067,"object_to_goal_dist_start":0.15068,"object_z_max":0.22725,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52534,-0.01665,0.17665],"tcp_start":[0.52353,-0.01521,0.18752],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":91.0,"n_steps_budget":600.0,"object_pos_end":[0.53059,-0.01687,0.2018],"object_pos_start":[0.53038,-0.01666,0.21633],"object_to_goal_dist_end":0.12671,"object_to_goal_dist_start":0.14067,"object_z_max":0.21633,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.52514,-0.01686,0.16218],"tcp_start":[0.52534,-0.01665,0.17665],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.53738,-0.00974,0.08407],"object_pos_start":[0.53059,-0.01687,0.2018],"object_to_goal_dist_end":0.03885,"object_to_goal_dist_start":0.12671,"object_z_max":0.2018,"peak_contact_force":10968.66931,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":10968.66931,"subtask_id":"insertion","tcp_end":[0.51707,0.00148,0.04471],"tcp_start":[0.51824,0.00083,0.04674],"tcp_to_object_dist_end":0.04569,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":405.0,"n_steps_budget":630.0,"object_pos_end":[0.53175,-0.0092,0.11895],"object_pos_start":[0.53552,-0.00876,0.0787],"object_to_goal_dist_end":0.05109,"object_to_goal_dist_start":0.0366,"object_z_max":0.11888,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":397.0,"raw_peak_contact_force":16311.90144,"tcp_end":[0.51287,0.00105,0.08522],"tcp_start":[0.51707,0.00148,0.04471],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41121,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.02191,"approach_entry.approach_speed":0.07995,"descend_to_contact.descend_offset":0.08903,"insert_peg.insert_speed":0.00653,"insert_peg.insertion_depth":0.03913,"retreat.retract_speed":0.06933},"optimized_scores":{"best_composite_score":0.3133,"best_fitness_score":0.7033,"best_task_score":0.91908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":48.0,"contact_point_centroid":[0.53141,-0.01326,0.04683],"force_p95":16154.21606,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16770.17122,"mean_force":4728.02355,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51952,-0.00838,0.05137]},{"body_a":"attachment","body_b":"peg_socket","contact_count":79.0,"contact_point_centroid":[0.52047,0.0067,0.0688],"force_p95":10047.41327,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10864.58396,"mean_force":1612.98381,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51896,-0.00778,0.06563]},{"body_a":"attachment","body_b":"peg_socket","contact_count":189.0,"contact_point_centroid":[0.50631,-0.00985,0.07111],"force_p95":8456.66118,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10539.65051,"mean_force":866.82349,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51945,-0.008,0.06448]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53259,-0.01263,0.0494],"force_p95":5178.53084,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5178.53084,"mean_force":5178.53084,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52097,-0.00686,0.05633]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.52429,0.00708,0.06344],"force_p95":3693.71513,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3991.19401,"mean_force":2004.50073,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52283,-0.00709,0.06052]}],"total_contact_groups":5},"final_pose_error":0.01031,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51566,-0.0067,0.09368],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":16770.17122,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.53447,-0.02097,0.2266],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15205,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52989,-0.02096,0.18686],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":166.0,"n_steps_budget":600.0,"object_pos_end":[0.53741,-0.023,0.21533],"object_pos_start":[0.53447,-0.02097,0.2266],"object_to_goal_dist_end":0.14228,"object_to_goal_dist_start":0.15205,"object_z_max":0.2266,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.53235,-0.02298,0.17565],"tcp_start":[0.52989,-0.02096,0.18686],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":32.0,"n_steps_budget":600.0,"object_pos_end":[0.53739,-0.02308,0.21101],"object_pos_start":[0.53741,-0.023,0.21533],"object_to_goal_dist_end":0.13818,"object_to_goal_dist_start":0.14228,"object_z_max":0.21533,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.53212,-0.02306,0.17136],"tcp_start":[0.53235,-0.02298,0.17565],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.54023,-0.01559,0.09525],"object_pos_start":[0.53739,-0.02308,0.21101],"object_to_goal_dist_end":0.04577,"object_to_goal_dist_start":0.13818,"object_z_max":0.21101,"peak_contact_force":1.41421,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":5178.53084,"subtask_id":"insertion","tcp_end":[0.51964,-0.00688,0.0532],"tcp_start":[0.52097,-0.00686,0.05633],"tcp_to_object_dist_end":0.04763,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.53443,-0.01609,0.12773],"object_pos_start":[0.53797,-0.01625,0.08749],"object_to_goal_dist_end":0.06102,"object_to_goal_dist_start":0.04197,"object_z_max":0.12766,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":316.0,"raw_peak_contact_force":16770.17122,"tcp_end":[0.51566,-0.0067,0.09368],"tcp_start":[0.51964,-0.00688,0.0532],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.19417,"average_mean_iterations":40.95631,"average_solve_count":206.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.03462,"approach_entry.approach_speed":0.02636,"descend_to_contact.descend_offset":0.10582,"insert_peg.insert_speed":0.01995,"insert_peg.insertion_depth":0.04427,"retreat.retract_speed":0.09924},"optimized_scores":{"best_composite_score":0.27284,"best_fitness_score":0.66284,"best_task_score":0.83332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":23.0,"contact_point_centroid":[0.55364,-0.00053,-0.00295],"force_p95":6400.84278,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6449.94982,"mean_force":3399.86605,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54161,-0.00057,0.00306]},{"body_a":"attachment","body_b":"peg_socket","contact_count":44.0,"contact_point_centroid":[0.52993,-0.00033,0.0306],"force_p95":6185.81303,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6281.00139,"mean_force":1802.97055,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.5417,-0.00041,0.02177]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52958,3e-05,0.06795],"force_p95":883.10842,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.10842,"mean_force":883.10842,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.54122,-3e-05,0.05942]},{"body_a":"attachment","body_b":"peg_socket","contact_count":201.0,"contact_point_centroid":[0.53015,-9e-05,0.06846],"force_p95":108.24745,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":812.49829,"mean_force":97.08278,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54237,-0.00017,0.05995]}],"total_contact_groups":4},"final_pose_error":0.01086,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.53614,-0.0002,0.09485],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":6449.94982,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.47559,-6e-05,0.22965],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15163,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.47103,-7e-05,0.18991],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.47407,-7e-05,0.22458],"object_pos_start":[0.47559,-6e-05,0.22965],"object_to_goal_dist_end":0.14689,"object_to_goal_dist_start":0.15163,"object_z_max":0.22965,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.46929,-8e-05,0.18487],"tcp_start":[0.47103,-7e-05,0.18991],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.47308,-8e-05,0.22292],"object_pos_start":[0.47407,-7e-05,0.22458],"object_to_goal_dist_end":0.14544,"object_to_goal_dist_start":0.14689,"object_z_max":0.22458,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.46813,-9e-05,0.18323],"tcp_start":[0.46929,-8e-05,0.18487],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.56334,0.00019,0.08756],"object_pos_start":[0.47308,-8e-05,0.22292],"object_to_goal_dist_end":0.06379,"object_to_goal_dist_start":0.14544,"object_z_max":0.22292,"peak_contact_force":845.47658,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":883.10842,"subtask_id":"insertion","tcp_end":[0.54022,-7e-05,0.05492],"tcp_start":[0.54022,-7e-05,0.05492],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55971,6e-05,0.12717],"object_pos_start":[0.56334,0.00019,0.08756],"object_to_goal_dist_end":0.07609,"object_to_goal_dist_start":0.06379,"object_z_max":0.1271,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":268.0,"raw_peak_contact_force":6449.94982,"tcp_end":[0.53614,-0.0002,0.09485],"tcp_start":[0.54022,-7e-05,0.05492],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```