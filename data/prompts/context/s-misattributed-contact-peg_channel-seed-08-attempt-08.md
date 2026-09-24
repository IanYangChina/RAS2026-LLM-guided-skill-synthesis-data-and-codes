## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0281 | 0.46 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0915 | 0.47 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1052 | 0.52 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1028 | 0.52 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1579 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=-0.028) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_push
- id: push_to_goal
  type: push
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_goal
- id: retract_tool
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
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
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_tool** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.028
- **task_score** (E): 0.456
- **fitness_score**: 0.482  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1787 |
| descend_to_contact | 1.00 | 1.00 | 0.1110 |
| push_to_goal | 0.00 | 0.67 | 0.0424 |
| retract_tool | 1.00 | 1.00 | 0.0676 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.146) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.507 | 10.703 |
| descend_to_contact | descend | 1.00 / step_budget | (0.513, 0.115, 0.146)→(0.500, 0.109, 0.037) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 4.000 | 18.434 | 42.831 |
| push_to_goal | push | 0.00 / guard_failure | (0.496, 0.011, 0.035)→(0.495, -0.031, 0.033) | (0.503, 0.079, 0.034)→(0.508, -0.058, 0.036) | 0.159→0.032 | 0.67 / 0.667 | 0.329 | 71.570 |
| retract_tool | retract | 1.00 / step_budget | (0.495, -0.031, 0.033)→(0.495, -0.073, 0.080) | (0.508, -0.058, 0.036)→(0.499, -0.068, 0.035) | 0.032→0.014 | 1.00 / 1.000 | 0.542 | 3.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.185
- terminal_score: 0.884
- phase_score: 0.402
- phase_breakdown.pre_push_score: 0.124
- phase_breakdown.push_goal_score: 0.521

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.884
- **Median Q (composite search score)**: -0.064
- **K-run variance**: 0.0066
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.1857,"descend_to_contact.descend_speed":0.02207,"descend_to_contact.descend_tolerance":0.003,"push_to_goal.force_threshold":41.55636,"push_to_goal.lateral_offset":-0.00196,"push_to_goal.push_distance":0.15984,"push_to_goal.push_speed":0.03908,"push_to_goal.push_tolerance":0.01331,"retract_tool.retract_speed":0.1216},"optimized_scores":{"best_composite_score":0.08452,"best_fitness_score":0.59452,"best_task_score":0.88372},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":952.0,"contact_point_centroid":[0.49606,0.06625,0.03191],"force_p95":37.151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.7344,"mean_force":26.12307,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48804,0.07445,0.032]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":905.0,"contact_point_centroid":[0.5255,0.05041,0.02773],"force_p95":29.24658,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.06587,"mean_force":22.61373,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48796,0.071,0.03192]},{"body_a":"peg","body_b":"channel_base_body","contact_count":770.0,"contact_point_centroid":[0.49636,0.11667,0.00946],"force_p95":0.85347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.91887,"mean_force":0.65122,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48679,0.14995,0.09013]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.49656,-0.00159,0.03703],"force_p95":25.07692,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.84107,"mean_force":15.33836,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48732,0.00535,0.03852]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.49399,0.13668,0.05926],"force_p95":4.43828,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.37912,"mean_force":1.99811,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49061,0.14858,0.04652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":526.0,"contact_point_centroid":[0.50246,-0.03556,0.00884],"force_p95":13.40822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.90186,"mean_force":4.13027,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49061,-0.02713,0.05599]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52546,-0.01347,0.0285],"force_p95":21.36418,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.61049,"mean_force":12.57363,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48744,0.00365,0.03937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":909.0,"contact_point_centroid":[0.50735,0.03875,0.00991],"force_p95":17.14597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.04408,"mean_force":12.78721,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48806,0.07281,0.03203]},{"body_a":"peg","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.51465,-0.0003,0.06917],"force_p95":11.66027,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.37741,"mean_force":5.34691,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48789,0.01962,0.03256]},{"body_a":"peg","body_b":"link7","contact_count":727.0,"contact_point_centroid":[0.51621,0.0437,0.06818],"force_p95":13.10361,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.20044,"mean_force":6.5102,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48792,0.06105,0.03196]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47499,-0.07149,0.02433],"force_p95":8.58275,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81285,"mean_force":3.27619,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49522,-0.06936,0.07943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.4962,0.11907,0.0094],"force_p95":0.63548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56039,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49136,0.17507,0.22014]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49943,0.19882,0.29705]}],"total_contact_groups":13},"final_pose_error":0.01193,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49363,-0.04743,0.02474],"final_tcp_position":[0.49567,-0.07291,0.08144],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":40.7344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":427.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11912,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48768,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":819.0,"raw_peak_contact_force":27.91887,"subtask_id":"pre_push","tcp_end":[0.48458,0.15251,0.14911],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.49577,0.11825,0.03482],"object_pos_start":[0.49606,0.11912,0.03393],"object_to_goal_dist_end":0.19836,"object_to_goal_dist_start":0.19925,"object_z_max":0.03486,"peak_contact_force":24.10189,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3493.0,"raw_peak_contact_force":40.7344,"subtask_id":"pre_push","tcp_end":[0.49158,0.14826,0.0359],"tcp_start":[0.48458,0.15251,0.14911],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50799,-0.00422,0.03971],"object_pos_start":[0.49577,0.11825,0.03482],"object_to_goal_dist_end":0.0762,"object_to_goal_dist_start":0.19836,"object_z_max":0.03978,"peak_contact_force":0.65012,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":987.0,"raw_peak_contact_force":27.84107,"subtask_id":"push_goal","tcp_end":[0.48864,0.02135,0.03235],"tcp_start":[0.49158,0.14826,0.0359],"tcp_to_object_dist_end":0.0329,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":559.0,"n_steps_budget":630.0,"object_pos_end":[0.49363,-0.04743,0.02474],"object_pos_start":[0.50799,-0.00422,0.03971],"object_to_goal_dist_end":0.03653,"object_to_goal_dist_start":0.0762,"object_z_max":0.04083,"peak_contact_force":0.49752,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":426.0,"raw_peak_contact_force":2.24822,"subtask_id":"push_goal","tcp_end":[0.49567,-0.07291,0.08144],"tcp_start":[0.48864,0.02135,0.03235],"tcp_to_object_dist_end":0.06219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.63878,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06408,"descend_to_contact.descend_speed":0.0186,"descend_to_contact.descend_tolerance":0.0049,"push_to_goal.force_threshold":45.12176,"push_to_goal.lateral_offset":0.0007,"push_to_goal.push_distance":0.16036,"push_to_goal.push_speed":0.03245,"push_to_goal.push_tolerance":0.01232,"retract_tool.retract_speed":0.14102},"optimized_scores":{"best_composite_score":-0.0642,"best_fitness_score":0.4458,"best_task_score":0.28716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":465.0,"contact_point_centroid":[0.49936,-0.07072,0.05783],"force_p95":93.19324,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.73498,"mean_force":61.87995,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49303,-0.06182,0.05362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50788,-0.10141,0.0593],"force_p95":74.2281,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.5737,"mean_force":52.86375,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49307,-0.06218,0.05459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.52559,-0.08493,0.05898],"force_p95":56.08513,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.29126,"mean_force":32.62888,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.4926,-0.06266,0.0569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":52.0,"contact_point_centroid":[0.5062,-0.1012,0.04551],"force_p95":42.21362,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.89726,"mean_force":24.64131,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49832,-0.05595,0.03412]},{"body_a":"attachment","body_b":"peg","contact_count":700.0,"contact_point_centroid":[0.50309,0.00113,0.04208],"force_p95":18.70355,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.54459,"mean_force":4.45487,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49919,0.01261,0.03412]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.4749,-0.07929,0.0325],"force_p95":17.87427,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.1778,"mean_force":8.5504,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49293,-0.0676,0.0747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":508.0,"contact_point_centroid":[0.50657,-0.03261,0.0099],"force_p95":9.01813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.13465,"mean_force":4.20915,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49924,0.01158,0.03419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50828,-0.09119,0.00991],"force_p95":14.31357,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.77415,"mean_force":3.90039,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49684,-0.05771,0.03436]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":512.0,"contact_point_centroid":[0.52507,-0.01436,0.02685],"force_p95":3.43026,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.35174,"mean_force":0.95262,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49913,0.01441,0.03402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":621.0,"contact_point_centroid":[0.50581,0.06297,0.00936],"force_p95":0.56101,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56835,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51176,0.14773,0.21823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49988,0.19799,0.29674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50594,0.0624,0.00939],"force_p95":0.55373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27704,"mean_force":0.55958,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.513,0.09589,0.09107]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50634,0.08087,0.05759],"force_p95":1.74399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.95092,"mean_force":1.00421,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50415,0.09295,0.04124]}],"total_contact_groups":13},"final_pose_error":0.0139,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50217,-0.07825,0.04046],"final_tcp_position":[0.4946,-0.07268,0.0795],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":93.73498,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.49413,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":2.27704,"subtask_id":"pre_push","tcp_end":[0.52454,0.09942,0.14535],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06278,0.03406],"object_pos_start":[0.50596,0.06295,0.03381],"object_to_goal_dist_end":0.14303,"object_to_goal_dist_start":0.14321,"object_z_max":0.03406,"peak_contact_force":17.4076,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1772.0,"raw_peak_contact_force":45.89726,"subtask_id":"pre_push","tcp_end":[0.5036,0.09278,0.03811],"tcp_start":[0.52454,0.09942,0.14535],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.50714,-0.08587,0.03482],"object_pos_start":[0.50602,0.06278,0.03406],"object_to_goal_dist_end":0.0106,"object_to_goal_dist_start":0.14303,"object_z_max":0.03587,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1387.0,"raw_peak_contact_force":93.73498,"subtask_id":"push_goal","tcp_end":[0.49799,-0.05805,0.03369],"tcp_start":[0.49804,-0.05806,0.03376],"tcp_to_object_dist_end":0.02931,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50217,-0.07825,0.04046],"object_pos_start":[0.50718,-0.08591,0.03478],"object_to_goal_dist_end":0.00282,"object_to_goal_dist_start":0.01067,"object_z_max":0.04775,"peak_contact_force":0.55196,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":655.0,"raw_peak_contact_force":3.88411,"subtask_id":"push_goal","tcp_end":[0.4946,-0.07268,0.0795],"tcp_start":[0.49799,-0.05805,0.03369],"tcp_to_object_dist_end":0.04016,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94527,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.15275,"descend_to_contact.descend_speed":0.02533,"descend_to_contact.descend_tolerance":0.00629,"push_to_goal.force_threshold":41.12711,"push_to_goal.lateral_offset":-0.00124,"push_to_goal.push_distance":0.15046,"push_to_goal.push_speed":0.04041,"push_to_goal.push_tolerance":0.01578,"retract_tool.retract_speed":0.08971},"optimized_scores":{"best_composite_score":-0.10459,"best_fitness_score":0.40541,"best_task_score":0.1963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":466.0,"contact_point_centroid":[0.49925,-0.07041,0.05803],"force_p95":91.90967,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.13465,"mean_force":59.79422,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49286,-0.06148,0.0539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50795,-0.10126,0.05984],"force_p95":73.02586,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.46113,"mean_force":51.03604,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49291,-0.06183,0.0548]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":457.0,"contact_point_centroid":[0.5255,-0.08459,0.0589],"force_p95":55.22419,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.78609,"mean_force":27.83665,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49277,-0.06166,0.05455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.50754,-0.10079,0.0509],"force_p95":39.97699,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.86089,"mean_force":23.56486,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49785,-0.05546,0.03427]},{"body_a":"attachment","body_b":"peg","contact_count":624.0,"contact_point_centroid":[0.50325,-0.0005,0.04282],"force_p95":13.86376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.15716,"mean_force":4.224,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49926,0.01095,0.03422]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47489,-0.07916,0.03263],"force_p95":18.2465,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.15729,"mean_force":8.87907,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49293,-0.06755,0.07485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49862,-0.09384,0.0099],"force_p95":16.18231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.77673,"mean_force":7.23405,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49711,-0.05675,0.03393]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":542.0,"contact_point_centroid":[0.52512,-0.02488,0.02927],"force_p95":6.23976,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.09612,"mean_force":1.52294,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49904,0.00389,0.03414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.50594,-0.03455,0.00988],"force_p95":9.28786,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.20937,"mean_force":4.10472,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49931,0.0101,0.03429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.50589,0.05659,0.00935],"force_p95":0.61849,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57454,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51534,0.14421,0.21749]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50018,0.19736,0.29586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":545.0,"contact_point_centroid":[0.50607,0.05645,0.00938],"force_p95":0.58176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9145,"mean_force":0.55016,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51674,0.08976,0.09112]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50685,0.07459,0.0577],"force_p95":1.26508,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50281,"mean_force":0.5035,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50471,0.08666,0.0399]}],"total_contact_groups":13},"final_pose_error":0.01408,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50227,-0.07869,0.04089],"final_tcp_position":[0.49456,-0.07248,0.07941],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":93.13465,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":594.0,"n_steps_budget":840.0,"object_pos_end":[0.50612,0.05668,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13696,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53822,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":550.0,"raw_peak_contact_force":1.9145,"subtask_id":"pre_push","tcp_end":[0.53101,0.09331,0.14494],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.05651,0.03369],"object_pos_start":[0.50612,0.05668,0.03377],"object_to_goal_dist_end":0.13679,"object_to_goal_dist_start":0.13696,"object_z_max":0.03383,"peak_contact_force":13.79141,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1692.0,"raw_peak_contact_force":41.86089,"subtask_id":"pre_push","tcp_end":[0.50434,0.08657,0.03828],"tcp_start":[0.53101,0.09331,0.14494],"tcp_to_object_dist_end":0.03045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.50759,-0.08425,0.03487],"object_pos_start":[0.50606,0.05651,0.03369],"object_to_goal_dist_end":0.0101,"object_to_goal_dist_start":0.13679,"object_z_max":0.03633,"peak_contact_force":0.33647,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1441.0,"raw_peak_contact_force":93.13465,"subtask_id":"push_goal","tcp_end":[0.49753,-0.05688,0.0339],"tcp_start":[0.49758,-0.05688,0.03396],"tcp_to_object_dist_end":0.02918,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50227,-0.07869,0.04089],"object_pos_start":[0.5076,-0.08432,0.03482],"object_to_goal_dist_end":0.00277,"object_to_goal_dist_start":0.01016,"object_z_max":0.04792,"peak_contact_force":0.57769,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":602.0,"raw_peak_contact_force":4.44541,"subtask_id":"push_goal","tcp_end":[0.49456,-0.07248,0.07941],"tcp_start":[0.49753,-0.05688,0.0339],"tcp_to_object_dist_end":0.03978,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```