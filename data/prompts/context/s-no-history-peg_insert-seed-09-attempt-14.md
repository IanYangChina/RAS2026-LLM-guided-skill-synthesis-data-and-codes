## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.306) — your mutation base

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

- **Composite score**: 0.306
- **task_score** (E): 0.889
- **fitness_score**: 0.696  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 1.00 | 0.00 | 0.1166 |
| align_to_socket | 1.00 | 0.00 | 0.0093 |
| descend_to_contact | 1.00 | 0.00 | 0.0064 |
| insert_peg | 0.00 | 1.00 | 0.0017 |
| retreat | 1.00 | 0.00 | 0.0408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.012, 0.188) | (0.504, -0.000, 0.340)→(0.513, -0.012, 0.228) | 0.260→0.152 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_socket | align | 1.00 / step_budget | (0.508, -0.012, 0.188)→(0.509, -0.013, 0.179) | (0.513, -0.012, 0.228)→(0.514, -0.013, 0.219) | 0.152→0.143 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_contact | descend | 1.00 / step_budget | (0.509, -0.013, 0.179)→(0.509, -0.013, 0.176) | (0.514, -0.013, 0.219)→(0.514, -0.013, 0.215) | 0.143→0.140 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_peg | insert | 0.00 / guard_failure | (0.528, -0.004, 0.050)→(0.528, -0.004, 0.049) | (0.514, -0.013, 0.215)→(0.549, -0.014, 0.085) | 0.140→0.053 | 1.00 / 1.333 | 3601.612 | 3805.090 |
| retreat | retract | 1.00 / step_budget | (0.528, -0.004, 0.049)→(0.524, -0.004, 0.089) | (0.548, -0.013, 0.081)→(0.545, -0.013, 0.121) | 0.051→0.063 | 0.00 / 0.000 | 0.000 | 7178.229 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.918
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.918
- phase_score: 0.596
- phase_breakdown.reach_socket_entry_score: 0.545
- phase_breakdown.insertion_score: 0.647

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.725
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.918
- **Median Q (composite search score)**: 0.308
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54717,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.05476,"approach_entry.approach_speed":0.07324,"descend_to_contact.descend_offset":0.08238,"insert_peg.insert_speed":0.04285,"insert_peg.insertion_depth":0.03601,"retreat.retract_speed":0.09622},"optimized_scores":{"best_composite_score":0.33513,"best_fitness_score":0.72513,"best_task_score":0.9184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53509,-0.01438,0.04806],"force_p95":1938.32686,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1971.17054,"mean_force":1667.48587,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52365,-0.00823,0.05363]},{"body_a":"attachment","body_b":"peg_socket","contact_count":50.0,"contact_point_centroid":[0.52738,-0.01056,0.04688],"force_p95":649.38608,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1036.77706,"mean_force":205.12199,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51696,-0.00446,0.05265]}],"total_contact_groups":2},"final_pose_error":0.01034,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51691,-0.00654,0.08893],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1971.17054,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.52816,-0.01519,0.22748],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15091,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52359,-0.01518,0.18774],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":102.0,"n_steps_budget":600.0,"object_pos_end":[0.53022,-0.01659,0.21681],"object_pos_start":[0.52816,-0.01519,0.22748],"object_to_goal_dist_end":0.14109,"object_to_goal_dist_start":0.15091,"object_z_max":0.22748,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52521,-0.01658,0.17713],"tcp_start":[0.52359,-0.01518,0.18774],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.53049,-0.01683,0.20407],"object_pos_start":[0.53022,-0.01659,0.21681],"object_to_goal_dist_end":0.12887,"object_to_goal_dist_start":0.14109,"object_z_max":0.21681,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.52509,-0.01682,0.16444],"tcp_start":[0.52521,-0.01658,0.17713],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.54111,-0.01771,0.08796],"object_pos_start":[0.53049,-0.01683,0.20407],"object_to_goal_dist_end":0.04547,"object_to_goal_dist_start":0.12887,"object_z_max":0.20407,"peak_contact_force":1388.55332,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":1971.17054,"subtask_id":"insertion","tcp_end":[0.52098,-0.00679,0.04843],"tcp_start":[0.52209,-0.00741,0.05051],"tcp_to_object_dist_end":0.04569,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.53576,-0.01686,0.12266],"object_pos_start":[0.53938,-0.01708,0.08242],"object_to_goal_dist_end":0.05817,"object_to_goal_dist_start":0.043,"object_z_max":0.1226,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":50.0,"raw_peak_contact_force":1036.77706,"tcp_end":[0.51691,-0.00654,0.08893],"tcp_start":[0.52098,-0.00679,0.04843],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34286,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.01811,"approach_entry.approach_speed":0.07148,"descend_to_contact.descend_offset":0.10652,"insert_peg.insert_speed":0.04976,"insert_peg.insertion_depth":0.04427,"retreat.retract_speed":0.05328},"optimized_scores":{"best_composite_score":0.30809,"best_fitness_score":0.69809,"best_task_score":0.91259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":51.0,"contact_point_centroid":[0.52863,-0.01363,0.04661],"force_p95":12430.54582,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13968.58435,"mean_force":3421.73391,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.5204,-0.00659,0.0536]},{"body_a":"attachment","body_b":"peg_socket","contact_count":150.0,"contact_point_centroid":[0.5233,0.00675,0.07067],"force_p95":9460.20464,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10650.29207,"mean_force":1023.32911,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51952,-0.00656,0.06524]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.5337,-0.01453,0.04794],"force_p95":8181.44826,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8554.37026,"mean_force":5058.22607,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52491,-0.00681,0.05526]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.52732,0.00706,0.05889],"force_p95":7556.13326,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7752.1196,"mean_force":5792.25617,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.52405,-0.00611,0.05352]},{"body_a":"attachment","body_b":"peg_socket","contact_count":147.0,"contact_point_centroid":[0.50643,-0.01059,0.07368],"force_p95":143.61253,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6235.9123,"mean_force":300.73315,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51939,-0.00674,0.0673]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.58903,-0.06854,0.07964],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.51898,-0.00411,0.0471]}],"total_contact_groups":6},"final_pose_error":0.01025,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51834,-0.00435,0.0905],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":13968.58435,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.53438,-0.02097,0.22653],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15197,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.52977,-0.02095,0.1868],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":172.0,"n_steps_budget":600.0,"object_pos_end":[0.53743,-0.02301,0.21528],"object_pos_start":[0.53438,-0.02097,0.22653],"object_to_goal_dist_end":0.14224,"object_to_goal_dist_start":0.15197,"object_z_max":0.22653,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.53234,-0.02299,0.17561],"tcp_start":[0.52977,-0.02095,0.1868],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.53835,-0.0233,0.2194],"object_pos_start":[0.53743,-0.02301,0.21528],"object_to_goal_dist_end":0.14644,"object_to_goal_dist_start":0.14224,"object_z_max":0.21938,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.53278,-0.02327,0.17979],"tcp_start":[0.53234,-0.02299,0.17561],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.5436,-0.02319,0.08615],"object_pos_start":[0.53835,-0.0233,0.2194],"object_to_goal_dist_end":0.04976,"object_to_goal_dist_start":0.14644,"object_z_max":0.2194,"peak_contact_force":8554.37026,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":8554.37026,"subtask_id":"insertion","tcp_end":[0.52224,-0.00471,0.04998],"tcp_start":[0.52334,-0.00552,0.0521],"tcp_to_object_dist_end":0.0459,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":402.0,"n_steps_budget":600.0,"object_pos_end":[0.53819,-0.02188,0.12047],"object_pos_start":[0.54172,-0.02216,0.08024],"object_to_goal_dist_end":0.0598,"object_to_goal_dist_start":0.04724,"object_z_max":0.12041,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":353.0,"raw_peak_contact_force":13968.58435,"tcp_end":[0.51834,-0.00435,0.0905],"tcp_start":[0.52224,-0.00471,0.04998],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.28369,"average_mean_iterations":58.9078,"average_solve_count":141.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.02509,"approach_entry.approach_speed":0.10881,"descend_to_contact.descend_offset":0.10177,"insert_peg.insert_speed":0.03997,"insert_peg.insertion_depth":0.04676,"retreat.retract_speed":0.03646},"optimized_scores":{"best_composite_score":0.27475,"best_fitness_score":0.66475,"best_task_score":0.83635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":25.0,"contact_point_centroid":[0.55419,-0.00031,-0.00327],"force_p95":6485.87046,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6529.32624,"mean_force":2643.90431,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54229,-0.00037,0.00259]},{"body_a":"attachment","body_b":"peg_socket","contact_count":74.0,"contact_point_centroid":[0.53016,-0.00016,0.03574],"force_p95":6035.89639,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6364.33093,"mean_force":926.68781,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54213,-0.00024,0.02688]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52954,2e-05,0.06041],"force_p95":889.72845,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":889.72845,"mean_force":889.72845,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.54103,-3e-05,0.05174]},{"body_a":"attachment","body_b":"peg_socket","contact_count":396.0,"contact_point_centroid":[0.53021,-9e-05,0.06668],"force_p95":94.49937,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":829.86211,"mean_force":86.88918,"phase_index":4.0,"phase_name":"retreat","phase_type":"retract","tcp_position_centroid":[0.54242,-0.00017,0.05808]}],"total_contact_groups":4},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.53578,-0.0002,0.08822],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":6529.32624,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":341.0,"n_steps_budget":720.0,"object_pos_end":[0.47571,-6e-05,0.22968],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15163,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.47117,-7e-05,0.18994],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":600.0,"object_pos_end":[0.47413,-7e-05,0.22458],"object_pos_start":[0.47571,-6e-05,0.22968],"object_to_goal_dist_end":0.14688,"object_to_goal_dist_start":0.15163,"object_z_max":0.22968,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_socket_entry","tcp_end":[0.46937,-8e-05,0.18487],"tcp_start":[0.47117,-7e-05,0.18994],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.47325,-7e-05,0.22263],"object_pos_start":[0.47413,-7e-05,0.22458],"object_to_goal_dist_end":0.14511,"object_to_goal_dist_start":0.14688,"object_z_max":0.22458,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.46832,-8e-05,0.18293],"tcp_start":[0.46937,-8e-05,0.18487],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.56342,0.00017,0.07966],"object_pos_start":[0.47325,-7e-05,0.22263],"object_to_goal_dist_end":0.06342,"object_to_goal_dist_start":0.14511,"object_z_max":0.22263,"peak_contact_force":861.91237,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":889.72845,"subtask_id":"insertion","tcp_end":[0.53992,-7e-05,0.0473],"tcp_start":[0.53992,-7e-05,0.0473],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":789.0,"n_steps_budget":870.0,"object_pos_end":[0.55971,5e-05,0.12026],"object_pos_start":[0.56342,0.00017,0.07966],"object_to_goal_dist_end":0.07202,"object_to_goal_dist_start":0.06342,"object_z_max":0.12021,"peak_contact_force":0.0,"phase_name":"retreat","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":495.0,"raw_peak_contact_force":6529.32624,"tcp_end":[0.53578,-0.0002,0.08822],"tcp_start":[0.53992,-7e-05,0.0473],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```