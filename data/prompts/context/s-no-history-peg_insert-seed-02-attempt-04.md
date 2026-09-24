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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen socket pose: [0.4809289707399447, -0.016120708526870135, 0.025] (static fixture for this episode)
- Goal object position: (0.4809289707399447, -0.016120708526870135, 0.025)
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
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_fixtures: {'peg_socket': [0.4809289707399447, -0.016120708526870135, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.862, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.4809289707399447, -0.016120708526870135, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.4809289707399447, -0.016120708526870135, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.123) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_target
  offset:
  - 0.0
  - 0.0
  - 0.065
  weight: 0.3
- id: insert_target
  metric: goal_progress
  weight: 0.7
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
    - 0.065
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.09
      default: 0.065
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_target
- id: descend_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.055
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_target
- id: insert_down
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.1
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: insert_target

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.065]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_contact** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_down** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.1
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.123
- **task_score** (E): 0.842
- **fitness_score**: 0.433  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.33 | 1.00 | 0.1369 |
| descend_to_entry | 0.33 | 1.00 | 0.0277 |
| contact_rim | 1.00 | 1.00 | 0.0001 |
| insert_down | 0.00 | 1.00 | 0.0302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.459, -0.005, 0.170) | (0.504, -0.000, 0.340)→(0.495, -0.005, 0.154) | 0.260→0.075 | 1.00 / 1.333 | 270.271 | 1256.630 |
| descend_to_entry | descend | 0.33 / step_budget | (0.459, -0.005, 0.170)→(0.473, -0.006, 0.193) | (0.495, -0.005, 0.154)→(0.506, -0.007, 0.170) | 0.075→0.091 | 1.00 / 1.000 | 318.479 | 441.721 |
| contact_rim | contact | 1.00 / force_exceeded | (0.473, -0.006, 0.193)→(0.473, -0.006, 0.193) | (0.506, -0.007, 0.170)→(0.506, -0.006, 0.170) | 0.091→0.091 | 1.00 / 1.000 | 338.005 | 338.005 |
| insert_down | insert | 0.00 / step_budget | (0.473, -0.006, 0.193)→(0.468, 0.009, 0.187) | (0.506, -0.006, 0.170)→(0.500, 0.005, 0.166) | 0.091→0.090 | 1.00 / 1.000 | 330.027 | 406.278 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.882
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.882
- phase_score: 0.214
- phase_breakdown.approach_target_score: 0.675
- phase_breakdown.insert_target_score: 0.016

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.481
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.882
- **Median Q (composite search score)**: 0.104
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: approach_high.approach_speed
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`; realized-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.01923,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.14844,"approach_high.approach_speed":0.06242,"approach_high.approach_tolerance":0.00835,"contact_rim.contact_force_threshold":7.56551,"contact_rim.contact_speed":0.01198,"descend_to_entry.descend_height":0.06204,"descend_to_entry.descend_speed":0.03714,"descend_to_entry.descend_tolerance":0.01095,"insert_down.insert_speed":0.01766,"insert_down.insert_tolerance":0.01155},"optimized_scores":{"best_composite_score":0.1042,"best_fitness_score":0.4142,"best_task_score":0.83075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":585.0,"contact_point_centroid":[0.54026,-0.00219,0.07971],"force_p95":572.03944,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1433.15382,"mean_force":278.94967,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44723,-0.00569,0.17829]},{"body_a":"peg_socket","body_b":"link6","contact_count":188.0,"contact_point_centroid":[0.54078,-0.00864,0.07908],"force_p95":1035.35291,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1161.76138,"mean_force":397.08038,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45511,-0.00759,0.19345]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.44258,-0.00433,0.07794],"force_p95":829.61315,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":872.17459,"mean_force":128.72411,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4389,-0.00265,0.08976]},{"body_a":"peg_socket","body_b":"link6","contact_count":815.0,"contact_point_centroid":[0.54089,-0.01036,0.07989],"force_p95":327.48318,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.14791,"mean_force":323.72434,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46779,-0.00867,0.20761]},{"body_a":"peg_socket","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.5404,-0.00281,0.07995],"force_p95":194.08265,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.8997,"mean_force":138.97146,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46071,-0.00754,0.19729]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54089,-0.013,0.07996],"force_p95":348.21379,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.21379,"mean_force":348.21379,"phase_index":2.0,"phase_name":"contact_rim","phase_type":"contact","tcp_position_centroid":[0.46759,-0.01155,0.21086]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.5409,-0.01573,0.07997],"force_p95":322.00727,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.70509,"mean_force":319.15291,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.46661,-0.01629,0.21318]}],"total_contact_groups":7},"final_pose_error":0.13629,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46583,-0.02384,0.21523],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1433.15382,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49075,-0.00811,0.17191],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09272,"object_to_goal_dist_start":0.26034,"object_z_max":0.3443,"peak_contact_force":281.11855,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":786.0,"raw_peak_contact_force":1433.15382,"subtask_id":"approach_target","tcp_end":[0.45875,-0.00811,0.19591],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":816.0,"n_steps_budget":990.0,"object_pos_end":[0.49652,-0.01128,0.18324],"object_pos_start":[0.49075,-0.00811,0.17191],"object_to_goal_dist_end":0.10391,"object_to_goal_dist_start":0.09272,"object_z_max":0.18323,"peak_contact_force":327.76563,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":864.0,"raw_peak_contact_force":561.14791,"subtask_id":"approach_target","tcp_end":[0.46759,-0.01155,0.21086],"tcp_start":[0.45875,-0.00811,0.19591],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49651,-0.01123,0.18324],"object_pos_start":[0.49652,-0.01128,0.18324],"object_to_goal_dist_end":0.10391,"object_to_goal_dist_start":0.10391,"object_z_max":0.18324,"peak_contact_force":348.21379,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":348.21379,"subtask_id":"insert_target","tcp_end":[0.46758,-0.01149,0.21086],"tcp_start":[0.46759,-0.01155,0.21086],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49428,-0.0218,0.18719],"object_pos_start":[0.49651,-0.01123,0.18324],"object_to_goal_dist_end":0.10953,"object_to_goal_dist_start":0.10391,"object_z_max":0.18718,"peak_contact_force":322.03673,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":333.70509,"subtask_id":"insert_target","tcp_end":[0.46583,-0.02384,0.21523],"tcp_start":[0.46758,-0.01149,0.21086],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.02632,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.18553,"approach_high.approach_speed":0.02,"approach_high.approach_tolerance":0.01086,"contact_rim.contact_force_threshold":5.74659,"contact_rim.contact_speed":0.01201,"descend_to_entry.descend_height":0.0585,"descend_to_entry.descend_speed":0.02143,"descend_to_entry.descend_tolerance":0.00982,"insert_down.insert_speed":0.01826,"insert_down.insert_tolerance":0.01198},"optimized_scores":{"best_composite_score":0.09484,"best_fitness_score":0.40484,"best_task_score":0.814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":907.0,"contact_point_centroid":[0.52665,-0.00809,0.07983],"force_p95":281.66719,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1304.23134,"mean_force":276.1602,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44815,-0.0042,0.12319]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.43172,-0.00551,0.0786],"force_p95":796.70528,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":860.11652,"mean_force":174.73861,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.42871,-0.00295,0.09084]},{"body_a":"peg_socket","body_b":"link7","contact_count":998.0,"contact_point_centroid":[0.52676,-0.01486,0.07999],"force_p95":406.83767,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.04701,"mean_force":378.02185,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47102,0.01018,0.14738]},{"body_a":"world","body_b":"link6","contact_count":284.0,"contact_point_centroid":[0.66884,-0.02061,-2e-05],"force_p95":234.38596,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.23463,"mean_force":85.17229,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47094,0.00914,0.14751]},{"body_a":"world","body_b":"link6","contact_count":34.0,"contact_point_centroid":[0.66751,-0.00952,-0.00023],"force_p95":451.96043,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.84592,"mean_force":171.98693,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47019,-0.00795,0.15039]},{"body_a":"peg_socket","body_b":"link7","contact_count":358.0,"contact_point_centroid":[0.52674,-0.01143,0.07997],"force_p95":388.44332,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":449.00326,"mean_force":352.25847,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46429,-0.00774,0.14418]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52675,-0.01231,0.07998],"force_p95":386.04863,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.04863,"mean_force":386.04863,"phase_index":2.0,"phase_name":"contact_rim","phase_type":"contact","tcp_position_centroid":[0.46936,-0.00903,0.14977]}],"total_contact_groups":7},"final_pose_error":0.08186,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47544,0.04233,0.13108],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1304.23134,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48918,-0.00633,0.12005],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04196,"object_to_goal_dist_start":0.26034,"object_z_max":0.34409,"peak_contact_force":281.72494,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":1304.23134,"subtask_id":"approach_target","tcp_end":[0.44961,-0.00617,0.12587],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":780.0,"object_pos_end":[0.5047,-0.00997,0.13105],"object_pos_start":[0.48918,-0.00633,0.12005],"object_to_goal_dist_end":0.05223,"object_to_goal_dist_start":0.04196,"object_z_max":0.13141,"peak_contact_force":380.83015,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":392.0,"raw_peak_contact_force":458.84592,"subtask_id":"approach_target","tcp_end":[0.46936,-0.00903,0.14977],"tcp_start":[0.44961,-0.00617,0.12587],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.5047,-0.00992,0.13105],"object_pos_start":[0.5047,-0.00997,0.13105],"object_to_goal_dist_end":0.05222,"object_to_goal_dist_start":0.05223,"object_z_max":0.13105,"peak_contact_force":386.04863,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":386.04863,"subtask_id":"insert_target","tcp_end":[0.46937,-0.00895,0.14977],"tcp_start":[0.46936,-0.00903,0.14977],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50949,0.02841,0.11536],"object_pos_start":[0.5047,-0.00992,0.13105],"object_to_goal_dist_end":0.04634,"object_to_goal_dist_start":0.05222,"object_z_max":0.13117,"peak_contact_force":421.23809,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1282.0,"raw_peak_contact_force":553.04701,"subtask_id":"insert_target","tcp_end":[0.47544,0.04233,0.13108],"tcp_start":[0.46937,-0.00895,0.14977],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.07921,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_height":0.13894,"approach_high.approach_speed":0.10633,"approach_high.approach_tolerance":0.01726,"contact_rim.contact_force_threshold":8.92242,"contact_rim.contact_speed":0.01011,"descend_to_entry.descend_height":0.06788,"descend_to_entry.descend_speed":0.02874,"descend_to_entry.descend_tolerance":0.00993,"insert_down.insert_speed":0.01204,"insert_down.insert_tolerance":0.00591},"optimized_scores":{"best_composite_score":0.17117,"best_fitness_score":0.48117,"best_task_score":0.88179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47635,0.0001,0.0789],"force_p95":992.40256,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1032.50559,"mean_force":440.67456,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46649,0.00011,0.09014]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.57171,0.0016,0.07913],"force_p95":703.20301,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":994.50674,"mean_force":227.33965,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4522,4e-05,0.11422]},{"body_a":"peg_socket","body_b":"link6","contact_count":365.0,"contact_point_centroid":[0.59533,-0.00255,0.07978],"force_p95":269.6856,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":586.33502,"mean_force":240.12738,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45896,0.00019,0.16701]},{"body_a":"peg_socket","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.5954,-0.0025,0.07991],"force_p95":266.45026,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.08058,"mean_force":228.83398,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.45196,0.00503,0.19916]},{"body_a":"peg_socket","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.59537,-0.0028,0.07986],"force_p95":273.40564,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.16774,"mean_force":237.34203,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46377,0.00088,0.19455]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59542,-0.00238,0.07997],"force_p95":279.75109,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.75109,"mean_force":279.75109,"phase_index":2.0,"phase_name":"contact_rim","phase_type":"contact","tcp_position_centroid":[0.48346,0.00186,0.21958]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.55363,-0.0292,0.07938],"force_p95":70.12198,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.14941,"mean_force":12.46014,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45603,1e-05,0.09647]}],"total_contact_groups":7},"final_pose_error":0.15409,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.46288,0.00988,0.21564],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1032.50559,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50491,0.00055,0.17143],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09157,"object_to_goal_dist_start":0.26034,"object_z_max":0.34496,"peak_contact_force":247.96864,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":419.0,"raw_peak_contact_force":1032.50559,"subtask_id":"approach_target","tcp_end":[0.46879,0.00055,0.18863],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51536,0.0017,0.19544],"object_pos_start":[0.50491,0.00055,0.17143],"object_to_goal_dist_end":0.11647,"object_to_goal_dist_start":0.09157,"object_z_max":0.19716,"peak_contact_force":246.84198,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":989.0,"raw_peak_contact_force":305.16774,"subtask_id":"approach_target","tcp_end":[0.48346,0.00186,0.21958],"tcp_start":[0.46879,0.00055,0.18863],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51534,0.00167,0.1955],"object_pos_start":[0.51536,0.0017,0.19544],"object_to_goal_dist_end":0.11652,"object_to_goal_dist_start":0.11647,"object_z_max":0.19544,"peak_contact_force":279.75109,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":279.75109,"subtask_id":"insert_target","tcp_end":[0.48344,0.00184,0.21962],"tcp_start":[0.48346,0.00186,0.21958],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49665,0.008,0.19427],"object_pos_start":[0.51534,0.00167,0.1955],"object_to_goal_dist_end":0.1146,"object_to_goal_dist_start":0.11652,"object_z_max":0.1955,"peak_contact_force":246.80529,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":999.0,"raw_peak_contact_force":332.08058,"subtask_id":"insert_target","tcp_end":[0.46288,0.00988,0.21564],"tcp_start":[0.48344,0.00184,0.21962],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```